"""
###############################################################################
#  Copyright 2019, by the California Institute of Technology. ALL RIGHTS RESERVED.
#  United States Government Sponsorship acknowledged. Any commercial use must be
#  negotiated with the Office of Technology Transfer at the
#  California Institute of Technology.
#
#  This software may be subject to U.S. export control laws. By accepting this
#  software,
#  the user agrees to comply with all applicable U.S. export laws and regulations.
#  User has the responsibility to obtain export licenses, or other export
#  authority
#  as may be required before exporting such information to foreign countries
#  or providing access to foreign persons.
#
#  file:	reconstructor.py
#  author:	S. Felipe Fregoso
#  brief:	Perform reconstruction operations on images received.
###############################################################################
"""
import sys
import copy
import multiprocessing
import threading
import time
import queue
import numpy as np

from shampoo.reconstruction import (Hologram)
from shampoo.mask import (Circle, Mask)

from . import telemetry_iface_ag
from . import interface as Iface
from . import metadata_classes as MetaC
from .heartbeat import Heartbeat as HBeat


MP = multiprocessing.get_context('spawn')
class Reconstructor(MP.Process):
    """
    Reconstructor class.  Child of multiprocessing.Process
    """

    def __init__(self, inq, pub, _events, configfile=None, verbose=False):
        """
        Constructor of Reconstruction class

        When instantiated creates a 'Reconstructor' object which is a process.
        In order to run the process, the 'start' method must be called which in
        turn call the 'run' method.  Within 'run' the process blocks on the
        'inq' and process the messages based on their type.  If the processing
        mode is not "IDLE" then it will reconstruct the image, signal the
        "done" event, and pass the reconstruction product to all the subscribers
        of the 'reconst_product' data.

        The reconstruction process occurs in the function "perform_reconstruction"

        Parameters
        ----------
        inq : 	multiprocessing.queues.Queue
            Input message queue for the process
        pub :	dhmpubsub.PubSub
            Handle to the publish/subscribe object
        _events :  multiprocessing.synchronize.Event
            Event to signal when reconstruct of an image has completed
        verbose : boolean
            If TRUE print detail information to terminal, FALSE otherwise.

        Returns
        -------
        None
            No return value
        """

        MP.Process.__init__(self)

        self._id = 'reconstructor'.upper()
        self._verbose = verbose
        self._inq = inq
        self._pub = pub
        self._events = _events

        ### HBeat
        self._hbeat = None

        ### Read in value from the DEFAULT File
        meta = MetaC.MetadataDictionary(configfile)
        self._reconst_meta = meta.metadata['RECONSTRUCTION']
        self._holo_meta = meta.metadata['HOLOGRAM']
        self._fouriermask_meta = meta.metadata['FOURIERMASK']
        self._camera_meta = meta.metadata['CAMERA']
        self._session_meta = meta.metadata['SESSION']

        self._mask = None
        self.holo = None

        self._reconstprocessor = {}
        self._reconstprocessor['queue'] = None
        self._reconstprocessor['thread'] = None
        self._update_fourier_mask = False
        self._g_db = {}

    def publish_reconst_status(self, status_msg=None):
        """
        Publish reconstruction status.  Sets status message if passed
        """
        if status_msg:
            self._reconst_meta.status_msg = status_msg
        self._pub.publish('reconst_status',
                          Iface.MetadataPacket(self._reconst_meta),
                         )

    def publish_holo_status(self, status_msg=None):
        """
        Publish hologram status.  Sets status message if passed
        """
        if status_msg:
            self._holo_meta.status_msg = status_msg
        self._pub.publish('holo_status', Iface.MetadataPacket(self._holo_meta))

    def publish_fouriermask_status(self, status_msg=None):
        """
        Publish fourier mask status.  Sets status message if passed
        """
        if status_msg:
            self._fouriermask_meta.status_msg = status_msg
        self._pub.publish('fouriermask_status',
                          Iface.MetadataPacket(self._fouriermask_meta),
                         )

    def _process_fitting_mode_cmd(self, arg, reconst_meta):
        """
        Process the command that sets the fitting mode
        """
        validcmd = True
        if arg.lower() == 'none':
            arg = MetaC.ReconstructionMetadata.FittingMetadata.FITTING_MODE_NONE
            reconst_meta.fitting.mode = arg
        elif arg.lower() == '1d_segment':
            arg = MetaC.ReconstructionMetadata.FittingMetadata.FITTING_MODE_1D_SEGMENT
            reconst_meta.fitting.mode = arg
        elif arg.lower() == '2d_segment':
            arg = MetaC.ReconstructionMetadata.FittingMetadata.FITTING_MODE_2D_SEGMENT
            reconst_meta.fitting.mode = arg
        else:
            validcmd = False
            print('Unrecognized Fitting Mode: %s'%(arg))

        return validcmd

    def _process_fitting_method_cmd(self, arg, reconst_meta):
        """
        Process the command that sets the fitting method
        """
        validcmd = True
        if arg.lower() == 'none':
            arg = MetaC.ReconstructionMetadata.FittingMetadata.FITTING_METHOD_NONE
            reconst_meta.fitting.method = arg
        elif arg.lower() == 'polynomial':
            arg = MetaC.ReconstructionMetadata.FittingMetadata.FITTING_METHOD_POLYNOMIAL
            reconst_meta.fitting.method = arg
        else:
            validcmd = False
            print('Unrecognized Fitting Mode: %s'%(arg))

        return validcmd

    def process_processing_mode_cmd(self, opcode, arg, reconst_meta):
        """
        Process the processing mode command
        """
        validcmd = True

        if arg == 'off':
            reconst_meta.processing_mode = MetaC.ReconstructionMetadata.RECONST_NONE
        elif arg == 'amp':
            reconst_meta.processing_mode = MetaC.ReconstructionMetadata.RECONST_AMP
        elif arg == 'intensity':
            reconst_meta.processing_mode = MetaC.ReconstructionMetadata.RECONST_INTENSITY
        elif arg == 'phase':
            reconst_meta.processing_mode = MetaC.ReconstructionMetadata.RECONST_PHASE
        elif arg == 'amp_and_phase':
            reconst_meta.processing_mode = MetaC.ReconstructionMetadata.RECONST_AMP_AND_PHASE
        elif arg == 'int_and_phase':
            reconst_meta.processing_mode = MetaC.ReconstructionMetadata.RECONST_INT_AND_PHASE
        elif arg == 'all':
            reconst_meta.processing_mode = MetaC.ReconstructionMetadata.RECONST_ALL
        else:
            validcmd = False
            #processing_mode = reconst_meta.processing_mode
            reconst_meta.status_msg += \
                'ERROR. Parameter [%s] arg [%s] is unkown option.  '\
                %(opcode, repr(arg))

        return validcmd

    def process_phase_unwrp_cmd(self, value, reconst_meta):
        """
        Process Phase Unwrap Command
        """
        validcmd = True
        if value.lower() == 'none':
            value = MetaC.ReconstructionMetadata.PhaseUnwrappingMetadata.PHASE_UNWRAPPING_NONE
            reconst_meta.phase_unwrapping.algorithm = value
        else:
            validcmd = False
            print('Unrecognized Phase Unwrapping Algorithm')

        return validcmd

    def _process_reconst_commands(self, arg, reconst_meta):
        """
        Process the reconstructor commands
        """
        validcmd = True
        for param, value in arg.items():
            reconst_meta.status_msg += \
                'Received parameter [%s] with value [%s].  '\
                %(param, repr(value))
            ### Propagation Distance list of floats
            if param == 'propagation_distance':
                reconst_meta.propagation_distance = value
            ### Compute Spectral Peak
            elif param == 'compute_spectral_peak':
                reconst_meta.compute_spectral_peak = value
            ### Compute the Digital Phase Mask
            elif param == 'compute_digital_phase_mask':
                reconst_meta.compute_digital_phase_mask = value
            elif param == 'chromatic_shift':
                reconst_meta.chromatic_shift = value
            ### Reference Hologram Parameters
            elif param == 'ref_holo_path':
                reconst_meta.ref_holo.path = value
            elif param == 'ref_holo_save':
                reconst_meta.ref_holo.save = value
            elif param == 'ref_holo_averaging_sec':
                reconst_meta.ref_holo.averaging_sec = value
            elif param == 'ref_holo_averaging_enable':
                reconst_meta.ref_holo.averaging_enabled = value
            ### Phase Unwrapping Parameters
            elif param == 'phase_unwrapping_enable':
                reconst_meta.phase_unwrapping.enabled = value
            elif param == 'phase_unwrapping_algorithm':

                validcmd = self.process_phase_unwrp_cmd(value, reconst_meta)

            #### Reset Phase Mask
            elif param == 'reset_phase_mask':
                reconst_meta.phase_mask_reset = value

            ### Fitting Mode Parametes
            elif param == 'fitting_mode':

                validcmd = self._process_fitting_mode_cmd(value, reconst_meta)

            elif param == 'fitting_method':

                validcmd = self._process_fitting_method_cmd(value, reconst_meta)

            elif param == 'fitting_order':
                reconst_meta.fitting.order = value
            elif param == 'fitting_apply':
                reconst_meta.fitting_apply = value
            ### Region Of Interest
            elif param == 'roi_offset_x':
                reconst_meta.roi_x.offset = value
            elif param == 'roi_offset_y':
                reconst_meta.roi_y.offset = value
            elif param == 'roi_size_x':
                reconst_meta.roi_x.size = value
            elif param == 'roi_size_y':
                reconst_meta.roi_y.size = value
            ### Center Image Parameters
            elif param == 'center_image':
                reconst_meta.center_image.center = value
            elif param == 'center_image_and_tilt':
                reconst_meta.center_image.center_and_tilt = value
            elif param == 'center_max_value':
                reconst_meta.center_image.max_value = value
            elif param == 'center_wide_spectrum':
                reconst_meta.center_image.wide_spectrum = value

            ### Processing Mode
            elif param == 'processing_mode':

                validcmd = self.process_processing_mode_cmd(param,
                                                            value,
                                                            reconst_meta,
                                                           )

            ### Enable or disable storing of reconstruction data
            elif param == 'store_files':
                reconst_meta.store_files = value


            ### Unknown Parameter
            else:
                validcmd = False

        reconst_meta.status_msg += 'SUCCESS.' if validcmd else 'UNSUCCESSFUL'

        return validcmd

    def process_holo_cmd(self, arg, holo_meta):
        """
        Process Holo Commands
        """
        validcmd = True

        for param, value in arg.items():

            holo_meta.status_msg += \
                'Received parameter [%s] with value [%s].'\
                %(param, repr(value))

            ### Wavelength
            if param == 'wavelength':
                holo_meta.wavelength = value
            elif param == 'dx':
                holo_meta.dx = value
            elif param == 'dy':
                holo_meta.dy = value
            elif param == 'crop_fraction':
                holo_meta.crop_fraction = value
            elif param == 'rebin_factor':
                holo_meta.rebin_factor = value
            elif param == 'bgd_sub':
                holo_meta.bgd_sub = value
            elif param == 'bgd_file':
                holo_meta.bgd_file = value
            else:
                validcmd = False
                holo_meta.status_msg += \
                    'ERROR.  Unknown parameter [%s].'\
                    %(param)

        holo_meta.status_msg += 'SUCCESS.' if validcmd else 'UNSUCCESSFUL'

        return validcmd


    def _create_mask_circle_1(self, param, value, fmask_meta):
        """
        """
        validcmd = True

        if len(value) != 3:
            validcmd = False
            fmask_meta.status_msg += \
                'ERROR. Parameter [%s] value must be list of 3'\
                'elements. [%s]'%(param, repr(value))
        else:
            center_x, center_y, radius = value
            if len(fmask_meta.center_list) < 1:
                fmask_meta.center_list.append(Circle(center_x,
                                                     center_y,
                                                     radius,
                                                    )
                                             )
            fmask_meta.center_list[0] = Circle(center_x,
                                               center_y,
                                               radius,
                                              )
            fmask_meta.mask = Mask(self._camera_meta.N,
                                   fmask_meta.center_list[0:len(self._holo_meta.wavelength)])
            self._update_fourier_mask = True

        return validcmd

    def _create_mask_circle_2(self, param, value, fmask_meta):
        """
        """
        validcmd = True

        if len(value) != 3:
            validcmd = False
            fmask_meta.status_msg += \
            'ERROR. Parameter [%s] value must be list of 3 elements.'\
            ' [%s] '%(param, repr(value))
        else:
            center_x, center_y, radius = value
            if len(fmask_meta.center_list) < 2:
                fmask_meta.center_list.append(Circle(center_x,
                                                     center_y,
                                                     radius,
                                                    )
                                             )
            fmask_meta.center_list[1] = Circle(center_x,
                                               center_y,
                                               radius
                                              )
            fmask_meta.mask = Mask(self._camera_meta.N,
                                   fmask_meta.center_list[0:len(self._holo_meta.wavelength)])
            self._update_fourier_mask = True

        return validcmd

    def _create_mask_circle_3(self, param, value, fmask_meta):
        """
        """
        validcmd = True
        if len(value) != 3:
            validcmd = False
            fmask_meta.status_msg += \
                'ERROR. Parameter [%s] value must be list of 3 elements.'\
                ' [%s]'%(param, repr(value))
        else:
            center_x, center_y, radius = value
            if len(fmask_meta.center_list) < 3:
                fmask_meta.center_list.append(Circle(center_x,
                                                     center_y,
                                                     radius,
                                                    ),
                                             )
            fmask_meta.center_list[2] = Circle(center_x,
                                               center_y,
                                               radius)
            fmask_meta.mask = Mask(self._camera_meta.N,
                                   fmask_meta.center_list[0:len(self._holo_meta.wavelength)])
            self._update_fourier_mask = True

        return validcmd

    def process_fouriermask_cmd(self, arg, fmask_meta):
        """
        Process Fourier Mask Commands
        """
        validcmd = True

        for param, value in arg.items():

            fmask_meta.status_msg += \
                'Received parameter [%s] with value [%s].'\
                %(param, repr(value))

            ### Fourier Mask Circles
            if param == 'mask_circle_1':

                validcmd = self._create_mask_circle_1(param, value, fmask_meta)

            elif param == 'mask_circle_2':

                validcmd = self._create_mask_circle_2(param, value, fmask_meta)

            elif param == 'mask_circle_3':

                validcmd = self._create_mask_circle_3(param, value, fmask_meta)

            else:
                validcmd = False
                fmask_meta.status_msg += \
                    'ERROR.  Unknown parameter [%s].  '%(param)

        fmask_meta.status_msg += 'SUCCESS.' if validcmd else 'UNSUCCESSFUL'

        return validcmd

    def _process_commands(self, data):
        """ Process commands received. """

        # Get local copy of meta data
        reconst_meta = copy.copy(self._reconst_meta)
        holo_meta = copy.copy(self._holo_meta)
        fmask_meta = copy.copy(self._fouriermask_meta)

        cmd = data.get_cmd()

        for modid, arg in cmd.items():
            if modid == 'reconst':
                reconst_meta.status_msg = ''

                if not arg: ### Empty parameter list, send reconst status
                    self.publish_reconst_status(status_msg='SUCCESS')
                    break

                self._process_reconst_commands(arg, reconst_meta)

                self._reconst_meta = copy.copy(reconst_meta)
                self.publish_reconst_status()

            elif modid == 'holo':

                holo_meta.status_msg = ''
                if not arg: ### Empty parameter list, send reconst status
                    self.publish_holo_status("SUCCESS")
                    continue

                self.process_holo_cmd(arg, holo_meta)

                self._holo_meta = copy.copy(holo_meta)
                self.publish_holo_status()

            elif modid == 'fouriermask':
                fmask_meta.status_msg = ''
                if not arg: ### Empty parameter list, send reconst status
                    self.publish_fouriermask_status("SUCCESS")
                    continue

                self.process_fouriermask_cmd(arg, fmask_meta)

                self._fouriermask_meta = copy.copy(fmask_meta)
                self.publish_fouriermask_status()

    def holometa_to_telem(self):
        """
        Converts holo metadata to telemetry object.  Returns telemetry object
        """
        holo_telem = telemetry_iface_ag.Hologram_Telemetry()
        holo_telem.set_values(len(self._holo_meta.wavelength),
                              self._holo_meta.wavelength,
                              self._holo_meta.dx,
                              self._holo_meta.dy,
                              self._holo_meta.crop_fraction,
                              self._holo_meta.rebin_factor,
                              self._holo_meta.bgd_sub,
                              self._holo_meta.bgd_file
                             )
        return holo_telem

    def reconst_thread(self, inq):
        """
        Reconstruction thread which performs the reconstruction

        This thread is spawned in the "run" method. Upon receipt of data which
        is an image it will run the "perform_reconstruction" method.  See this
        method for details

        Parameters
        ----------
        inq  :  queue.Queue
            Queue used to recieve image data of type Iface.image
        Return
        ---------
        None

        """

        while True:
            try:
                data = inq.get()
                if data is None:
                    break
            except queue.Empty:
                pass

            self._reconst_meta.running = True
            self.perform_reconstruction(data)
            self._reconst_meta.running = False

    def _create_hologram_obj(self, img):
        """
        Create hologram object or update it if it already exists
        """
        ### Create Hologram object or update it.  Updating saves CPU cycles.
        if self.holo is None:
            self.holo = Hologram(img,
                                 wavelength=self._holo_meta.wavelength,
                                 crop_fraction=self._holo_meta.crop_fraction,
                                 rebin_factor=self._holo_meta.rebin_factor,
                                 dx=self._holo_meta.dx,
                                 dy=self._holo_meta.dy,
                                 mask=self._mask,
                                )
        else:
            self.holo.update_hologram(img,
                                      wavelength=self._holo_meta.wavelength,
                                      crop_fraction=self._holo_meta.crop_fraction,
                                      rebin_factor=self._holo_meta.rebin_factor,
                                      dx=self._holo_meta.dx,
                                      dy=self._holo_meta.dy,
                                      mask=self._mask
                                     )
            self._mask = self.holo.mask

    def _update_g_factor_db(self):
        """
        Update the G Factor database or add to database if entry doesn't exist
        """
        start_time = time.time()

        g_key = repr(self._reconst_meta.propagation_distance) + \
                "_" + repr(self.holo.n) + \
                "_" + repr(self._holo_meta.dx) + \
                "_" + repr(self._holo_meta.dy) + \
                "_" + repr(self._holo_meta.wavelength)

        try:

            prop_kernel = self._g_db[g_key]
            self.holo.set_G_factor(prop_kernel)

        except KeyError:

            if self._verbose:
                print('Updating G factor for g_key=%s'%(g_key))
            self.holo.update_G_factor(self._reconst_meta.propagation_distance)
            self._g_db[g_key] = self.holo.G

        if self._verbose:
            print('%f: Reconstruction G Database. Elapsed Time: %f'\
                  %(time.time(), time.time()-start_time))

    def _recompute_mask(self):
        """
        Inidicates if need to recompute mask
        """
        recompute_mask = False
        if self._mask is not None:
            recompute_mask = self._mask.shape[0] != self.holo.ft_hologram.shape[0] or\
                             self._mask.shape[1] != self.holo.ft_hologram.shape[1]
            print("%%%%%%%%%%%%%%%%%: ", self._mask.shape,
                  self.holo.ft_hologram.shape,
                  recompute_mask)

        return recompute_mask

    def _compute_spectral_peak(self, recompute_mask):
        """
        Find the spectral peak mathematically of the fourier image and create a mask around the peak
        The computed mask and peak locations are stored into self.holo.mask, self.holo.x_peak, and self.holo.y_peak
        """
        ### Compute the spectral peak and the mask
        if self._reconst_meta.compute_spectral_peak or recompute_mask:

            self.holo.x_peak,\
            self.holo.y_peak,\
            self._mask = self.holo.compute_spectral_peak_mask(mask_radius=150)

            self.holo.mask = self._mask
            self._reconst_meta.compute_spectral_peak = False
            print("((((((((((((((( Computing spectral peak:",
                  self.holo.mask.shape, self._mask.shape
                 )
        elif self._update_fourier_mask:
            print('Updating Fourier Mask...')
            self._update_fourier_mask = False

            if len(self._fouriermask_meta.center_list) > 0:

                print('Really Updating Fourier Mask...')
                idx = slice(0, len(self._holo_meta.wavelength))
                self._fouriermask_meta.mask = Mask(self.holo.n,
                                                   self._fouriermask_meta.center_list[idx])
                self.holo.x_peak = np.zeros((len(self._holo_meta.wavelength), 1), dtype=np.int)
                self.holo.y_peak = np.zeros((len(self._holo_meta.wavelength), 1), dtype=np.int)

                for _ in range(len(self._holo_meta.wavelength)):

                    self.holo.x_peak[_] = self._fouriermask_meta.center_list[_].centery
                    self.holo.y_peak[_] = self._fouriermask_meta.center_list[_].centerx

                self._mask = self._fouriermask_meta.mask.mask
                self.holo.mask = self._mask

    def _validate_wavelength_chromatic_shift(self):
        """
        Validate and ensure that aboth wavelength and chormatic shift
        are the same
        """
        wavelength = self._holo_meta.wavelength

        if len(wavelength) != len(self._reconst_meta.chromatic_shift):

            if len(self._reconst_meta.chromatic_shift) > len(wavelength):

                idx = slice(0, len(wavelength))
                self._reconst_meta.chromatic_shift = self._reconst_meta.chromatic_shift[idx]

            elif len(self._reconst_meta.chromatic_shift) < len(self._holo_meta.wavelength):

                tmpchromaticshift = [0] * len(wavelength)
                self._reconst_meta.chromatic_shift = [tmpchromaticshift[i]\
                                                      for i in range(len(wavelength))]

    def _reconstruct(self):
        """
        Performs reconstruction
        """
        prop_dist = self._reconst_meta.propagation_distance
        chromatic_shift = self._reconst_meta.chromatic_shift
        comp_dig_phase = self._reconst_meta.compute_digital_phase_mask
        www = self.holo.my_reconstruct(prop_dist,
                                       fourier_mask=None,
                                       compute_digital_phase_mask=comp_dig_phase,
                                       compute_spectral_peak=False,
                                       chromatic_shift=chromatic_shift,
                                      )
        return www

    def perform_reconstruction(self, data):
        """
        Perform the reconstruction of an image

        No reconstruction is performed if the processing_mode is RECONST_NONE
        and return immediately.
        Else, the following occurs:
            1.  a hologram object is created using metadata parameters.
                To save CPU cycles, the hologra object is updated if it
                already exists.
            2.  The FFT of the image is computed.
            3.  A query of the G factor database is done.  If nothing is found
                in the database, then the G is computed and database populated
                the the computed contents
            4.  If the mask is not the same shape as the FFT, then recompute
                the mask.
            5.  Compute the spectral peak or update the mask if requested or
                new mask available
            6.  Ensure that the wavelenght and the chromatic shift are of the
                same length
            7.  Compute the reconstruction
            8.  Publish the reconstruction results
            9.  Publish reconstruction done message

        Parameters
        ---------
        data :	Iface.Image
            Data containing an image

        Return
        ------
        None
            Nothing is returned

        """
        try:
            processing_mode = self._reconst_meta.processing_mode

            if processing_mode == MetaC.ReconstructionMetadata.RECONST_NONE:
                return

            start_time = time.time()
            if self._verbose:
                print("%f: &&&&&&&&&&&&&&&&&&&&&&&&&&& RECONSTRUCT !!!"\
                      %(time.time()))

            ### Get the image
            _, img = data.get_img()

            ### Create Hologram object or update it.  Updating saves CPU cycles.
            self._create_hologram_obj(img)

            ### Compute the Fourier Transform
            self.holo.ft_hologram

            ### Update the G Factor database
            self._update_g_factor_db()

            ### If mask shape not equal to ft_hologram, need to recompute mask
            recompute_mask = self._recompute_mask()

            ### Compute the spectral peak and the mask
            self._compute_spectral_peak(recompute_mask)

            ### Ensure that the wavelenght and the
            ### chromatic shift are of the same length
            self._validate_wavelength_chromatic_shift()

            ### Perform the reconstruction
            www = self._reconstruct()

            ### Compute product based on processing_mode
            if self._reconst_meta.processing_mode == MetaC.ReconstructionMetadata.RECONST_AMP:
                www.amplitude
            elif self._reconst_meta.processing_mode == MetaC.ReconstructionMetadata.RECONST_INTENSITY:
                www.intensity
            elif self._reconst_meta.processing_mode == MetaC.ReconstructionMetadata.RECONST_PHASE:
                www.phase
            elif self._reconst_meta.processing_mode == MetaC.ReconstructionMetadata.RECONST_AMP_AND_PHASE:
                www.amplitude
                www.phase
            elif self._reconst_meta.processing_mode == MetaC.ReconstructionMetadata.RECONST_INT_AND_PHASE:
                www.intensity
                www.phase
            else:
                www.intensity
                www.amplitude
                www.phase

            if self._verbose:
                print('<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<')
            print('%f: Reconstruction Computed . Elapsed Time: %f'\
                  %(time.time(), time.time()-start_time))

            fourier_image = np.log(np.abs(self.holo.ft_hologram)).astype(np.uint8)
            reconstproduct = Iface.ReconstructorProduct(img,
                                                        self.holo,
                                                        fourier_image,
                                                        www,
                                                        self._reconst_meta,
                                                        self._holo_meta,
                                                       )
            self._pub.publish('reconst_product', reconstproduct)
            self._pub.publish('reconst_done', Iface.MetadataPacket(MetaC.ReconstructionDoneMetadata(done=True)))

        except Exception as err:
            status_msg = "ERROR.  "
            status_msg += repr(err)
            self.publish_reconst_status(status_msg=status_msg)
            raise err

    def _init_recon_process_threads(self):
        """
        Initialize and start thread that will do the reconstruction
        """
        self._reconstprocessor['queue'] = queue.Queue()
        self._reconstprocessor['thread'] = threading.Thread(target=self.reconst_thread,
                                                            args=(self._reconstprocessor['queue'],),
                                                           )
        self._reconstprocessor['thread'].daemon = True
        self._reconstprocessor['thread'].start()

    def create_heartbeat(self):
        """
        Create the heartbeat object
        """
        self._hbeat = HBeat(self._pub, self._id.lower())

    def start_heartbeat(self):
        """
        Start the heartbeat
        """
        self._hbeat.start()

    def terminate_heartbeat(self):
        """
        End the execution of this components heartbeat
        """
        self._hbeat.terminate()

    def notify_controller_and_wait(self):
        """
        Notify the controller component that this component is ready
        and wait for controller component OK to start running
        """
        self._pub.publish('init_done', Iface.InitDonePkt('Reconstructor', 0))
        print('[%s] Consumer thread started'%(self._id))
        self._events['controller']['start'].wait()

    def _process_images(self, data):
        """
        Process images received from the camera server
        Place image in reconstructor processor queue for processing
        """
        print("Reconstructor received image")
        processing_mode = self._reconst_meta.processing_mode
        if processing_mode == MetaC.ReconstructionMetadata.RECONST_NONE:
            #continue
            pass
        elif not self._reconst_meta.running:
            print("%f: Reconstructor:  Got Image!"%(time.time()))
            self._reconst_meta.running = True
            self._reconstprocessor['queue'].put(data)
        else:
            pass

    def _process_component_messages(self, data):
        """
        Process the component messages per data type
        """
        ### Process command
        if isinstance(data, Iface.Command):

            self._process_commands(data)

        ### Process image (from camera streamer)
        elif isinstance(data, Iface.Image):

            self._process_images(data)

        elif isinstance(data, MetaC.HologramMetadata):

            self._holo_meta = data
            self.publish_holo_status()

        else:
            pass

    def run(self):
        """
        Reconstruction process loop.

        This function starts off by spawning the thread where the reconstruction will be done
        and creates a queue to feed that thread images.
        The heartbeat for the Reconstructor is created here.  All commands sent to the Reconstructor
        is received in the "self._inq" and processed.
        """

        try:
            #msPkt = Iface.CamServerFramePkt()

            self._init_recon_process_threads()

            self.create_heartbeat()

            self.notify_controller_and_wait()

            self.start_heartbeat()

            while True:
                data = self._inq.get()
                if data is None:
                    print('Exiting Reconstructor')
                    break

                ### Process command
                self._process_component_messages(data)

            ## End of While
            self.end_component()

        except Exception as err:

            self.handle_component_exception(err)

        finally:
            pass

    def end_component(self):
        """
        End execution of component
        """
        self.terminate_heartbeat()
        if self._hbeat.isAlive():
            self._hbeat.join(timeout=5)
        print('[%s]: End'%(self._id))

    def handle_component_exception(self, err):
        """
        Send Heartbeat error and raise the error
        """
        print('[%s] Exception caught: %s'%(self._id, repr(err)))
        exc_type, exc_obj, t_b = sys.exc_info()
        lineno = t_b.tb_lineno
        print('{} EXCEPTION IN (LINE {}): {}'.format(self._id, lineno, exc_obj))

        self._hbeat.set_update(err)
        if self._hbeat.isAlive():
            self._hbeat.join(timeout=5)
        raise err

###############################################################################
#  Copyright 2019, by the California Institute of Technology. ALL RIGHTS RESERVED. 
#  United States Government Sponsorship acknowledged. Any commercial use must be 
#  negotiated with the Office of Technology Transfer at the 
#  California Institute of Technology.
#
#  This software may be subject to U.S. export control laws. By accepting this software, 
#  the user agrees to comply with all applicable U.S. export laws and regulations. 
#  User has the responsibility to obtain export licenses, or other export authority 
#  as may be required before exporting such information to foreign countries or providing 
#  access to foreign persons.
#
#  file:	reconstructor.py
#  author:	S. Felipe Fregoso
#  brief:	Perform reconstruction operations on images received.
#               
#              
###############################################################################
import socket
import numpy as np
import copy
import select
import multiprocessing
import threading
import time
import queue

from . import metadata_classes
from . import interface
from . import telemetry_iface_ag
from .heartbeat import Heartbeat
from shampoo.reconstruction import (Hologram)
from shampoo.mask import (Circle, Mask)

mp = multiprocessing.get_context('spawn')
class Reconstructor(mp.Process):
    """ Reconstructor class.  Child of multiprocessing.Process"""

    def __init__(self, inq, pub, _events, configfile=None, verbose=False):
        """ 
        Constructor of Reconstruction class 

        When instantiated creates a 'Reconstructor' object which is a process.
        In order to run the process, the 'start' method must be called which in turn calls
        the 'run' method.  Within 'run' the process blocks on the 'inq' and process the messages
        based on their type.  If the processing mode is not "IDLE" then it will reconstruct the 
        image, signal the "done" event, and pass the reconstruction product to all the subscribers
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

        mp.Process.__init__(self)

        self._verbose = verbose
        self._inq = inq
        self._pub = pub
        self._events = _events

        ### Heartbeat
        self._HB = None

        ### Read in value from the DEFAULT File
        meta = metadata_classes.Metadata_Dictionary(configfile)
        self._reconst_meta = meta.metadata['RECONSTRUCTION']
        self._holo_meta    = meta.metadata['HOLOGRAM']
        self._fouriermask_meta = meta.metadata['FOURIERMASK']
        self._camera_meta = meta.metadata['CAMERA']

        self._mask = None
        self.holo = None

        self._reconstprocessor = {}
        self._reconstprocessor['queue'] = None
        self._reconstprocessor['thread'] = None
        self._update_fourier_mask = False
        self._G_database = {}

    def publish_reconst_status(self, status_msg=None):
        """ Publish reconstruction status.  Sets status message if passed """
        if status_msg:
            self._reconst_meta.status_msg = status_msg
        self._pub.publish('reconst_status', interface.MetadataPacket(self._reconst_meta))
    
    def publish_holo_status(self, status_msg=None):
        """ Publish hologram status.  Sets status message if passed """
        if status_msg:
            self._holo_meta.status_msg = status_msg
        self._pub.publish('holo_status', interface.MetadataPacket(self._holo_meta))
        #self._pub.publish('holo_telemetry', self.holometa_to_telem())

    def publish_fouriermask_status(self, status_msg=None):
        """ Publish fourier mask status.  Sets status message if passed """
        if status_msg:
            self._fouriermask_meta.status_msg = status_msg
        self._pub.publish('fouriermask_status', interface.MetadataPacket(self._fouriermask_meta))

    def process_commands(self, data):
        """ Process commands received. """
        tmpreconstmeta = copy.copy(self._reconst_meta)
        tmpholometa = copy.copy(self._holo_meta)
        tmpfouriermaskmeta = copy.copy(self._fouriermask_meta)
        cmd = data.get_cmd()
        for k, v in cmd.items():
            if k == 'reconst':
                tmpreconstmeta.status_msg = ''

                if not v: ### Empty parameter list, send reconst status
                    self.publish_reconst_status(status_msg = 'SUCCESS')
                    break

                validcmd = True
                for param,value in v.items():
                    tmpreconstmeta.status_msg += 'Received parameter [%s] with value [%s].  '%(param, repr(value))
                    ### Propagation Distance list of floats
                    if param == 'propagation_distance':
                        tmpreconstmeta.propagation_distance = value
                    ### Compute Spectral Peak
                    elif param == 'compute_spectral_peak':
                        tmpreconstmeta.compute_spectral_peak = value
                    ### Compute the Digital Phase Mask
                    elif param == 'compute_digital_phase_mask':
                        tmpreconstmeta.compute_digital_phase_mask = value
                    elif param == 'chromatic_shift':
                        tmpreconstmeta.chromatic_shift= value
                    ### Reference Hologram Parameters
                    elif param == 'ref_holo_path':
                        tmpreconstmeta.ref_holo.path= value
                    elif param == 'ref_holo_save':
                        tmpreconstmeta.ref_holo.save = value
                    elif param == 'ref_holo_averaging_sec':
                        tmpreconstmeta.ref_holo.averaging_sec = value
                    elif param == 'ref_holo_averaging_enable':
                        tmpreconstmeta.ref_holo.averaging_enabled= value
                    ### Phase Unwrapping Parameters
                    elif param == 'phase_unwrapping_enable':
                        tmpreconstmeta.phase_unwrapping.enabled= value
                    elif param == 'phase_unwrapping_algorithm':
                        if value.lower() == 'none':
                            value = metadata_classes.Reconstruction_Metadata.PhaseUnwrapping_Metadata.PHASE_UNWRAPPING_NONE
                            tmpreconstmeta.phase_unwrapping.algorithm = value
                        else:
                            print('Unrecognized Phase Unwrapping Algorithm')
                    #### Reset Phase Mask
                    elif param == 'reset_phase_mask':
                        tmpreconstmeta.phase_mask_reset = value
                    ### Fitting Mode Parametes
                    elif param == 'fitting_mode':
                        if value.lower() == 'none':
                            value = metadata_classes.Reconstruction_Metadata.Fitting_Metadata.FITTING_MODE_NONE
                            tmpreconstmeta.fitting.mode= value
                        elif value.lower() == '1d_segment':
                            value = metadata_classes.Reconstruction_Metadata.Fitting_Metadata.FITTING_MODE_1D_SEGMENT
                            tmpreconstmeta.fitting.mode= value
                        elif value.lower() == '2d_segment':
                            value = metadata_classes.Reconstruction_Metadata.Fitting_Metadata.FITTING_MODE_2D_SEGMENT
                            tmpreconstmeta.fitting.mode= value
                        else:
                            print('Unrecognized Fitting Mode: %s'%(value))
                    elif param == 'fitting_method':
                        if value.lower() == 'none':
                            value = metadata_classes.Reconstruction_Metadata.Fitting_Metadata.FITTING_METHOD_NONE
                            tmpreconstmeta.fitting.method = value
                        elif value.lower() == 'polynomial':
                            value = metadata_classes.Reconstruction_Metadata.Fitting_Metadata.FITTING_METHOD_POLYNOMIAL
                            tmpreconstmeta.fitting.method = value
                        else:
                            print('Unrecognized Fitting Mode: %s'%(value))
                    elif param == 'fitting_order':
                        tmpreconstmeta.fitting.order = value
                    elif param == 'fitting_apply':
                        tmpreconstmeta.fitting_apply = value
                    ### Region Of Interest
                    elif param == 'roi_offset_x':
                        tmpreconstmeta.roi_x.offset = value
                    elif param == 'roi_offset_y':
                        tmpreconstmeta.roi_y.offset = value
                    elif param == 'roi_size_x':
                        tmpreconstmeta.roi_x.size = value
                    elif param == 'roi_size_y':
                        tmpreconstmeta.roi_y.size = value
                    ### Center Image Parameters
                    elif param == 'center_image':
                        tmpreconstmeta.center_image.center = value
                    elif param == 'center_image_and_tilt':
                        tmpreconstmeta.center_image.center_and_tilt = value
                    elif param == 'center_max_value':
                        tmpreconstmeta.center_image.max_value = value
                    elif param == 'center_wide_spectrum':
                        tmpreconstmeta.center_image.wide_spectrum = value
                    
                    ### Processing Mode
                    elif param == 'processing_mode':
                        if value == 'off':
                            tmpreconstmeta.processing_mode = metadata_classes.Reconstruction_Metadata.RECONST_NONE
                        elif value == 'amp':
                            tmpreconstmeta.processing_mode = metadata_classes.Reconstruction_Metadata.RECONST_AMP
                        elif value == 'intensity':
                            tmpreconstmeta.processing_mode = metadata_classes.Reconstruction_Metadata.RECONST_INTENSITY
                        elif value == 'phase':
                            tmpreconstmeta.processing_mode = metadata_classes.Reconstruction_Metadata.RECONST_PHASE
                        elif value == 'amp_and_phase':
                            tmpreconstmeta.processing_mode = metadata_classes.Reconstruction_Metadata.RECONST_AMP_AND_PHASE
                        elif value == 'int_and_phase':
                            tmpreconstmeta.processing_mode = metadata_classes.Reconstruction_Metadata.RECONST_INT_AND_PHASE
                        elif value == 'all':
                            tmpreconstmeta.processing_mode = metadata_classes.Reconstruction_Metadata.RECONST_ALL
                        else:
                           validcmd = False
                           tmpreconstmeta.status_msg += 'ERROR. Parameter [%s] value [%s] is unkown option.  '%(param, repr(value))
                    ### Enable or disable storing of reconstruction data
                    elif param == 'store_files':
                        tmpreconstmeta.store_files = value


                    ### Unknown Parameter
                    else:
                        validcmd = False

                tmpreconstmeta.status_msg += 'SUCCESS.' if validcmd else 'UNSUCCESSFUL'
                
                self._reconst_meta = copy.copy(tmpreconstmeta)
                self.publish_reconst_status()

            elif k == 'holo':
                tmpholometa.status_msg = ''
                if not v: ### Empty parameter list, send reconst status
                    self.publish_holo_status("SUCCESS")
                    continue

                validcmd = True
                for param, value in v.items():
                    tmpholometa.status_msg += 'Received parameter [%s] with value [%s].  '%(param, repr(value))
                    ### Wavelength
                    if param == 'wavelength':
                        tmpholometa.wavelength = value
                    elif param == 'dx':
                        tmpholometa.dx = value
                    elif param == 'dy':
                        tmpholometa.dy = value
                    elif param == 'crop_fraction':
                        tmpholometa.crop_fraction = value
                    elif param == 'rebin_factor':
                        tmpholometa.rebin_factor = value
                    elif param == 'bgd_sub':
                        tmpholometa.bgd_sub = value
                    elif param == 'bgd_file':
                        tmpholometa.bgd_file = value
                    else:
                        validcmd = False
                        tmpholometa.status_msg += 'ERROR.  Unknown parameter [%s].  '%(param)
                        pass
                tmpholometa.status_msg += 'SUCCESS.' if validcmd else 'UNSUCCESSFUL'
                
                self._holo_meta = copy.copy(tmpholometa)
                self.publish_holo_status()

            elif k == 'fouriermask':
                tmpfouriermaskmeta.status_msg = ''
                if not v: ### Empty parameter list, send reconst status
                    self.publish_fouriermask_status("SUCCESS")
                    continue

                validcmd = True
                for param, value in v.items():
                    tmpfouriermaskmeta.status_msg += 'Received parameter [%s] with value [%s].  '%(param, repr(value))
                    ### Fourier Mask Circles
                    if param == 'mask_circle_1':
                        if len(value) != 3:
                            tmpfouriermaskmeta.status_msg += 'ERROR. Parameter [%s] value must be list of 3 elements.  '%(param, repr(value))
                        else:
                            center_x, center_y, radius = value
                            if len(tmpfouriermaskmeta.center_list) < 1:
                                tmpfouriermaskmeta.center_list.append(Circle(center_x, center_y, radius))
                            tmpfouriermaskmeta.center_list[0] = Circle(center_x, center_y, radius)
                            tmpfouriermaskmeta.mask = Mask(self._camera_meta.N, tmpfouriermaskmeta.center_list[0:len(self._holo_meta.wavelength)])
                            self._update_fourier_mask = True

                    elif param == 'mask_circle_2':
                        if len(value) != 3:
                            tmpfouriermaskmeta.status_msg += 'ERROR. Parameter [%s] value must be list of 3 elements.  '%(param, repr(value))
                        else:
                            center_x, center_y, radius = value
                            if len(tmpfouriermaskmeta.center_list) < 2:
                                tmpfouriermaskmeta.center_list.append(Circle(center_x, center_y, radius))
                            tmpfouriermaskmeta.center_list[1] = Circle(center_x, center_y, radius)
                            tmpfouriermaskmeta.mask = Mask(self._camera_meta.N, tmpfouriermaskmeta.center_list[0:len(self._holo_meta.wavelength)])
                            self._update_fourier_mask = True

                    elif param == 'mask_circle_3':
                        if len(value) != 3:
                            tmpfouriermaskmeta.status_msg += 'ERROR. Parameter [%s] value must be list of 3 elements.  '%(param, repr(value))
                        else:
                            center_x, center_y, radius = value
                            if len(tmpfouriermaskmeta.center_list) < 3:
                                tmpfouriermaskmeta.center_list.append(Circle(center_x, center_y, radius))
                            tmpfouriermaskmeta.center_list[2] = Circle(center_x, center_y, radius)
                            tmpfouriermaskmeta.mask = Mask(self._camera_meta.N, tmpfouriermaskmeta.center_list[0:len(self._holo_meta.wavelength)])
                            self._update_fourier_mask = True
                    else:
                        validcmd = False
                        tmpfouriermeta.status_msg += 'ERROR.  Unknown parameter [%s].  '%(param)
                        pass
                tmpfouriermaskmeta.status_msg += 'SUCCESS.' if validcmd else 'UNSUCCESSFUL'
                self._fouriermask_meta = copy.copy(tmpfouriermaskmeta)
                self.publish_fouriermask_status()

    def holometa_to_telem(self):
        """ Converts holo metadata to telemetry object.  Returns telemetry object"""
        holo_telem = telemetry_iface_ag.Hologram_Telemetry()
        holo_telem.set_values(len(self._holo_meta.wavelength),self._holo_meta.wavelength,self._holo_meta.dx,self._holo_meta.dy,self._holo_meta.crop_fraction,self._holo_meta.rebin_factor,self._holo_meta.bgd_sub,self._holo_meta.bgd_file)
        return holo_telem

    def reconst_thread(self, inq):
        """ 
        Reconstruction thread which performs the reconstruction 
        
        This thread is spawned in the "run" method. Upon receipt of data which is an image
        it will run the "perform_reconstruction" method.  See this method for details

        Parameters
        ----------
        inq  :  queue.Queue
            Queue used to recieve image data of type interface.image
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
            
    def perform_reconstruction(self, data):
        """
        Perform the reconstruction of an image

        No reconstruction is performed if the processing_mode is RECONST_NONE and return immediately.
        Else, the following occurs:
            1.  a hologram object is created using metadata parameters. To save CPU cycles, the hologra object is updated if it already exists.
            2.  The FFT of the image is computed.  
            3.  A query of the G factor database is done.  If nothing is found in the database, then the G is computed and database populated the the computed contents
            4.  If the mask is not the same shape as the FFT, then recompute the mask.
            5.  Compute the spectral peak or update the mask if requested or new mask available
            6.  Ensure that the wavelenght and the chromatic shift are of the same length
            7.  Compute the reconstruction
            8.  Publish the reconstruction results
            9.  Publish reconstruction done message
        
        Parameters
        ---------
        data :	interface.Image
            Data containing an image

        Return
        ------
        None
            Nothing is returned

        """
        try:
            if self._reconst_meta.processing_mode == metadata_classes.Reconstruction_Metadata.RECONST_NONE:
                return

            start_time = time.time()
            if self._verbose: print("%f: &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&& RECONSTRUCT !!!"%(time.time()))

            ### Get the image
            header, img = data.get_img()

            ### Create Hologram object or update it.  Updating saves CPU cycles.
            if self.holo is None:
                self.holo = Hologram(img, wavelength=self._holo_meta.wavelength, crop_fraction=self._holo_meta.crop_fraction, rebin_factor=self._holo_meta.rebin_factor, dx=self._holo_meta.dx, dy=self._holo_meta.dy, mask=self._mask)
            else:
                self.holo.update_hologram(img, wavelength=self._holo_meta.wavelength, crop_fraction=self._holo_meta.crop_fraction, rebin_factor=self._holo_meta.rebin_factor, dx=self._holo_meta.dx, dy=self._holo_meta.dy, mask=self._mask)
                self._mask = self.holo.mask

            holo = self.holo

            ### Compute the Fourier Transform
            holo.ft_hologram
            if self._verbose: print('%f: Reconstruction FT Hologram . Elapsed Time: %f'%(time.time(), time.time()-start_time))

            ### Update the G Factor database
            G_key = repr(self._reconst_meta.propagation_distance) + "_" + repr(holo.n) + "_" + repr(self._holo_meta.dx) + "_" + repr(self._holo_meta.dy) + "_" + repr(self._holo_meta.wavelength)
            try:
                G = self._G_database[G_key]
                holo.set_G_factor(G)
            except KeyError as e:
                if self._verbose: print('Updating G factor for G_key=%s'%(G_key))
                holo.update_G_factor(self._reconst_meta.propagation_distance)
                self._G_database[G_key]=holo.G

            if self._verbose: print('%f: Reconstruction G Database. Elapsed Time: %f'%(time.time(), time.time()-start_time))

            ### If mask shape not equal to ft_hologram, need to recompute mask
            recompute_mask = False
            if self._mask is not None:
                recompute_mask = self._mask.shape[0] != holo.ft_hologram.shape[0] or self._mask.shape[1] != holo.ft_hologram.shape[1]
                print("%%%%%%%%%%%%%%%%%: ", self._mask.shape, holo.ft_hologram.shape, recompute_mask)

            ### Compute the spectral peak and the mask
            if self._reconst_meta.compute_spectral_peak or recompute_mask:
                holo.x_peak, holo.y_peak, self._mask = holo.compute_spectral_peak_mask(mask_radius=150)
                holo.mask = self._mask
                self._reconst_meta.compute_spectral_peak = False
                print("((((((((((((((( Computing spectral peak:", holo.mask.shape, self._mask.shape)
            elif self._update_fourier_mask:
                print('Updating Fourier Mask...')
                self._update_fourier_mask = False
                if len(self._fouriermask_meta.center_list) > 0:
                    print('Really Updating Fourier Mask...')
                    self._fouriermask_meta.mask = Mask(holo.n, self._fouriermask_meta.center_list[0:len(self._holo_meta.wavelength)])
                    holo.x_peak = np.zeros((len(self._holo_meta.wavelength), 1), dtype=np.int)
                    holo.y_peak = np.zeros((len(self._holo_meta.wavelength), 1), dtype=np.int)
                    for _ in range(len(self._holo_meta.wavelength)):
                        holo.x_peak[_] = self._fouriermask_meta.center_list[_].centery
                        holo.y_peak[_] = self._fouriermask_meta.center_list[_].centerx
                    self._mask = self._fouriermask_meta.mask.mask
                    holo.mask = self._mask
                    pass


            ### Ensure that the wavelenght and the chromatic shift are of the same length
            if len(self._holo_meta.wavelength) != len(self._reconst_meta.chromatic_shift):
               if len(self._reconst_meta.chromatic_shift) > len(self._holo_meta.wavelength): 
                   self._reconst_meta.chromatic_shift = self._reconst_meta.chromatic_shift[0:len(self._holo_meta.wavelength)]
               elif len(self._reconst_meta.chromatic_shift) < len(self._holo_meta.wavelength):
                  tmpchromaticshift = [0] * len(self._holo_meta.wavelength)
                  self._reconst_meta.chromatic_shift = [tmpchromaticshift[i] for i in range(len(self._holo_meta.wavelength))]
            
            ### Perform the reconstruction
            w = holo.my_reconstruct(self._reconst_meta.propagation_distance, fourier_mask=None, compute_digital_phase_mask=self._reconst_meta.compute_digital_phase_mask, compute_spectral_peak=False, chromatic_shift=self._reconst_meta.chromatic_shift)

            ### Compute product based on processing_mode
            if self._reconst_meta.processing_mode == metadata_classes.Reconstruction_Metadata.RECONST_AMP:
                w.amplitude
            elif self._reconst_meta.processing_mode == metadata_classes.Reconstruction_Metadata.RECONST_INTENSITY:
                w.intensity
            elif self._reconst_meta.processing_mode == metadata_classes.Reconstruction_Metadata.RECONST_PHASE:
                w.phase
            elif self._reconst_meta.processing_mode == metadata_classes.Reconstruction_Metadata.RECONST_AMP_AND_PHASE:
                w.amplitude
                w.phase
            elif self._reconst_meta.processing_mode == metadata_classes.Reconstruction_Metadata.RECONST_INT_AND_PHASE:
                w.intensity
                w.phase
            else:
                w.intensity
                w.amplitude
                w.phase

            if self._verbose:  print('<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<')
            #if self._verbose:  print('%f: Reconstruction Computed . Elapsed Time: %f'%(time.time(), time.time()-start_time))
            if True:  print('%f: Reconstruction Computed . Elapsed Time: %f'%(time.time(), time.time()-start_time))

            reconstproduct = interface.ReconstructorProduct(img, holo, np.log(np.abs(holo.ft_hologram)).astype(np.uint8), w, self._reconst_meta, self._holo_meta)
            self._pub.publish('reconst_product', reconstproduct)
            self._pub.publish('reconst_done', interface.MetadataPacket(metadata_classes.Reconstruction_Done_Metadata(done=True)))
        except Exception as e:
            status_msg = "ERROR.  "
            status_msg += repr(e)
            self.publish_reconst_status(status_msg = status_msg)
            raise e
            
    def run(self):
        """
        Reconstruction process loop.

        This function starts off by spawning the thread where the reconstruction will be done
        and creates a queue to feed that thread images.
        The heartbeat for the Reconstructor is created here.  All commands sent to the Reconstructor
        is received in the "self._inq" and processed.
        """

        try:
            self._reconstprocessor['queue'] = queue.Queue()
            self._reconstprocessor['thread'] = threading.Thread(target = self.reconst_thread, args=(self._reconstprocessor['queue'],))
            self._reconstprocessor['thread'].daemon = True
            self._reconstprocessor['thread'].start()
            ### Initalize and start the heartbeat
            self._HB = Heartbeat(self._pub, 'reconstructor')
    
    
            msPkt = interface.CamServerFramePkt()
    
            self._pub.publish('init_done', interface.InitDonePkt('Reconstructor', 0))
            print('Reconstructor Consumer thread started')

            self._events['controller']['start'].wait()

            print('Reconstructor received init_done')
            self._HB.start()
            while True:
                data = self._inq.get()
                if data is None:
                    print('Exiting Reconstructor')
                    break
    
                ### Process command
                if type(data) is interface.Command:
                    self.process_commands(data)
                    pass
    
                ### Process image (from camera streamer)
                elif type(data) is interface.Image:
                    print("Reconstructor received image")
                    if self._reconst_meta.processing_mode == metadata_classes.Reconstruction_Metadata.RECONST_NONE:
                        continue

                    elif self._reconst_meta.running == False:
                        print("%f: Reconstructor:  Got Image!"%(time.time()))
                        self._reconst_meta.running = True
                        self._reconstprocessor['queue'].put(data)

                elif type(data) is metadata_classes.Hologram_Metadata:
                    self._holo_meta = data 
                    self.publish_holo_status()
            ## End of While
            self._HB.terminate()

        except Exception as e:

            self._HB.set_update(e)
            if self._HB.isAlive():
                self._HB.join(timeout=5)

            raise e
        finally:
            pass


"""
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
#  file:	metadata_classes.py
#  author:	S. Felipe Fregoso
#  description:	Contains all metadata classes used for the dhmsw
#               The metadata classes created correspond to the
#               commands in the command dictionary (although not always)
###############################################################################
"""
import time
import configparser
from abc import ABC, abstractmethod

from shampoo_lite.mask import (Circle, Mask)

class MetadataABC(ABC):
    """
    Abstract class for all Metadata classes
    """
    # pylint: disable=too-few-public-methods
    @abstractmethod
    def load_config(self, filepath):
        """
        Load config file abstract method
        Ensures all subclasses define this method
        """
        while False:
            yield None

class MetadataDictionary():
    """
    Class for holding in a dictionary all metadata objects
    used by the dhmsw
    """
    def __init__(self, configfile=None):
        """
        Constructor
        """
        self.metadata = {}
        self.metadata['CONTROLLER'] = ControllerMetadata()
        self.metadata['HEARTBEAT'] = HeartbeatMetadata()
        self.metadata['GUISERVER'] = GuiserverMetadata()
        self.metadata['DATALOGGER'] = DataloggerMetadata()
        self.metadata['CAMERA'] = CameraMetadata()
        self.metadata['FRAMESOURCE'] = FramesourceMetadata()
        self.metadata['WATCHDOG'] = WatchdogMetadata()
        self.metadata['HOLOGRAM'] = HologramMetadata()
        self.metadata['RECONSTRUCTION'] = ReconstructionMetadata()
        self.metadata['FOURIERMASK'] = FouriermaskMetadata()
        self.metadata['SESSION'] = SessionMetadata()

        self._config_file = configfile

        #for k in self.metadata.keys():
        #    self.metadata[k].load_config(configfile)
        for _, comp_meta in self.metadata.items():
            comp_meta.load_config(configfile)

    def get_meta_dict(self):
        """
        Return the dictionary of metadatas
        """
        return self.metadata

    def get_config_file(self):
        """
        Return the config file
        """
        return self._config_file

class ControllerMetadata(MetadataABC):
    """
    Class for Controller component metadata
    """
    def __init__(self, configfile=None, cmd_hostname='localhost', cmd_port=10000):

        self.cmd_hostname = cmd_hostname
        self.cmd_port = cmd_port

        self.load_config(configfile)

        self._id = 'CONTROLLER'

    def load_config(self, filepath):
        """
        Read the config file and load data pertaining to this metadata
        """
        if filepath is None:
            return

        try:
            config = configparser.ConfigParser()
            dataset = config.read(filepath)

            if not dataset:
                raise ValueError("File [%s] doesn't exist."%(filepath))

            cmd_hostname = config.get(self._id, 'cmd_hostname', fallback='localhost')
            cmd_port = config.getint(self._id, 'cmd_port', fallback=10000)

            self.cmd_hostname = cmd_hostname
            self.cmd_port = cmd_port

        except configparser.Error as err:
            print('File read error:  [%s] due to error [%s]. Key=[%s].'\
                  %(filepath, repr(err), self._id))
            raise err('Config file read error:  [%s] due to error [%s]. Key=[%s].'\
                  %(filepath, repr(err), self._id))

    def get_hostname(self):
        """
        Return the hostname
        """
        return self.cmd_hostname

    def get_port(self):
        """
        Return the port
        """
        return self.cmd_port

class HeartbeatMetadata(MetadataABC):
    """
    Heartbeat Metadata class
    """
    def __init__(self):
        """
        Constructor
        """
        self.ident = ''
        self.timestamp = time.time()
        self.exception = None

    def load_config(self, filepath):
        """
        Read the config file and load data pertaining to this metadata
        """

    def get_timestamp(self):
        """
        Return timestamp
        """
        return self.timestamp

class GuiserverMetadata(MetadataABC):
    """
    GUI Server Metadata class
    """
    def __init__(self, configfile=None):
        """
        Constructor
        """
        self.connection_status = [False, False, False, False, False, False]

        self.enabled = {'rawframes':True,
                        'fourier':True,
                        'reconst_amp':True,
                        'reconst_intensity':True,
                        'reconst_phase':True,
                       }

        self.ports = {'fourier':9993,
                      'reconst_amp':9994,
                      'raw_frames':9995,
                      'telemetry':9996,
                      'reconst_intensity':9997,
                      'reconst_phase':9998}

        self.hostname = '127.0.0.1'
        self.maxclients = 5
        self.status_msg = ''

        self.load_config(configfile)

    def get_connection_status(self):
        """
        Return the connection status array
        """
        return self.connection_status

    def get_enabled_state(self):
        """
        Return enabled state
        """
        return self.enabled

    def load_config(self, filepath):
        """
        Read the config file and load data pertaining to this metadata
        """

        if filepath is None:
            return

        key = 'GUISERVER'
        try:
            config = configparser.ConfigParser()
            dataset = config.read(filepath)

            if not dataset:
                raise ValueError("File [%s] doesn't exist."%(filepath))

            fourier_port = config.getint(key, 'fourier_port', fallback=9993)
            reconst_amp_port = config.getint(key, 'reconst_amp_port', fallback=9994)
            raw_frames_port = config.getint(key, 'raw_frames_port', fallback=9995)
            telemetry_port = config.getint(key, 'telemetry_port', fallback=9996)
            reconst_intensity_port = config.getint(key, 'reconst_intensity_port', fallback=9997)
            reconst_phase_port = config.getint(key, 'reconst_phase_port', fallback=9998)
            host = config.get(key, 'host', fallback='127.0.0.1')
            maxclients = config.getint(key, 'maxclients', fallback=5)

            self.ports['fourier'] = fourier_port
            self.ports['reconst_amp'] = reconst_amp_port
            self.ports['raw_frames'] = raw_frames_port
            self.ports['telemetry'] = telemetry_port
            self.ports['reconst_intensity'] = reconst_intensity_port
            self.ports['reconst_phase'] = reconst_phase_port
            self.hostname = host
            self.maxclients = maxclients

        except configparser.Error as err:
            print('File read error:  [%s] due to error [%s]. Key=[%s].'\
                  %(filepath, repr(err), key))

class DataloggerMetadata(MetadataABC):
    """
    Data logger metadata class
    """
    def __init__(self, configfile=None):
        self.enabled = True
        self.status_msg = ''

        self.load_config(configfile)

    def get_enabled(self):
        """
        Return enabled flag
        """
        return self.enabled

    def load_config(self, filepath):
        """
        Read the config file and load data pertaining to this metadata
        """

        key = 'DATALOGGER'
        if filepath is None:
            return

        try:
            config = configparser.ConfigParser()
            dataset = config.read(filepath)

            if not dataset:
                raise ValueError("File [%s] doesn't exist."%(filepath))

            enabled = config.getboolean(key, 'enabled', fallback=False)
            self.enabled = enabled

        except configparser.Error as err:
            print('File read error:  [%s] due to error [%s]. Key=[%s].'\
                  %(filepath, repr(err), key))

class CameraMetadata(MetadataABC):
    """
    Camera Metadata Class
    """
    def __init__(self, N=2048, rate=15.0, shutter=15000,
                 gain=0, roi_pos=(0, 0), roi_size=(2048, 2048)):
        """
        Constructor
        """
        self.N = N
        self.rate = rate
        self.shutter = shutter
        self.gain = gain
        self.roi_pos = roi_pos
        self.roi_size = roi_size
        self.status_msg = ''

    def get_camera_params(self):
        """
        Return the camera parameters
        """
        return (self.N, self.rate, self.shutter, self.gain,
                self.roi_pos, self.roi_size)

    def load_config(self, filepath):
        """
        Read the config file and load data pertaining to this metadata
        """

        key = 'CAMERA'
        if filepath is None:
            return

        try:
            config = configparser.ConfigParser()
            dataset = config.read(filepath)

            if not dataset:
                raise ValueError("File [%s] doesn't exist."%(filepath))

            N = config.getint(key, 'N', fallback=2048)
            rate = config.getfloat(key, 'rate', fallback=15.0)
            shutter = config.getint(key, 'shutter', fallback=15000)
            gain = config.getint(key, 'gain', fallback=0)
            roi_pos_x = config.getint(key, 'roi_pos_x', fallback=0)
            roi_pos_y = config.getint(key, 'roi_pos_y', fallback=0)
            roi_size_x = config.getint(key, 'roi_size_x', fallback=N)
            roi_size_y = config.getint(key, 'roi_size_y', fallback=N)

            self.N = N
            self.rate = rate
            self.shutter = shutter
            self.gain = gain
            self.roi_pos = (roi_pos_x, roi_pos_y)
            self.roi_size = (roi_size_x, roi_size_y)

        except configparser.Error as err:
            print('File read error:  [%s] due to error [%s]. Key=[%s].'\
                  %(filepath, repr(err), key))

class CameraServerMetadata(MetadataABC):
    """
    Camera server metadata Class
    """
    def __init__(self, configfile=None):
        """
        Constructor
        """
        self.host = '127.0.0.1'
        base_port = 2000
        self.ports = {'frame':base_port, 'command':base_port+1, 'telemetry':base_port+2}
        self.status_msg = ''

        self.load_config(configfile)

    def get_ports(self):
        """
        Return the ports for the camera server
        """
        return self.ports

    def load_config(self, filepath):
        """
        Read the config file and load data pertaining to this metadata
        """
        if filepath is None:
            return

        key = 'CAMERA_SERVER'
        try:
            config = configparser.ConfigParser()
            dataset = config.read(filepath)

            if not dataset:
                raise ValueError("File [%s] doesn't exist."%(filepath))

            host = config.get(key, 'host', fallback='127.0.0.1')
            frame_port = config.getint(key, 'frame', fallback=2000)
            command_port = config.getint(key, 'command', fallback=2001)
            telemetry_port = config.getint(key, 'telemetry', fallback=2002)

            self.host = host
            self.ports['frame'] = frame_port
            self.ports['command'] = command_port
            self.ports['telemetry'] = telemetry_port

        except configparser.Error as err:
            print('File read error:  [%s] due to error [%s]. Key=[%s].'\
                  %(filepath, repr(err), key))

class FramesourceMetadata(MetadataABC):
    """
    Framesource metadata class
    """
    FRAMESOURCE_FILE = 0  # Don't compute the reconstruction
    FRAMESOURCE_MICROSCOPE = 1  # Don't compute the reconstruction

    FRAMESOURCE_STATE_IDLE = 0
    FRAMESOURCE_STATE_RUNNING = 1

    def __init__(self, configfile=None):
        """
        Constructor
        """
        self.state = self.FRAMESOURCE_STATE_IDLE
        self.mode = ''
        self.camserver = CameraServerMetadata(configfile=configfile)
        self.file = {}
        self.file['datadir'] = '/proj/dhm/sfregoso/git_repos/dhmsw/simulated_frames/*.bmp'
        self.file['currentfile'] = '/proj/dhm/sfregoso/git_repos/dhmsw/simulated_frames/*.bmp'
        self.status_msg = ''

        self.load_config(configfile)

    def get_state(self):
        """
        Return the state
        """
        return self.state

    def load_config(self, filepath):
        """
        Read the config file and load data pertaining to this metadata
        """
        if filepath is None:
            return

        key = 'FRAMESOURCE'
        try:
            config = configparser.ConfigParser()
            dataset = config.read(filepath)

            if not dataset:
                raise ValueError("File [%s] doesn't exist."%(filepath))

            datadir = config.get(key, 'datadir', fallback='')
            self.datadir = datadir

        except configparser.Error as err:
            print('File read error:  [%s] due to error [%s]. Key=[%s].'\
                  %(filepath, repr(err), key))

class WatchdogMetadata(MetadataABC):
    """
    Watchdog Metadata Class
    """
    def __init__(self):
        """
        Constructor
        """
        self.status_msg = ''

    def load_config(self, filepath):
        """
        Read the config file and load data pertaining to this metadata
        """

    def get_status_msg(self):
        """
        Return the status message
        """
        return self.status_msg

class HologramMetadata(MetadataABC):
    """
    Hologram Metadata Class
    """
    def __init__(self):
        """
        Constructor
        """
        self.wavelength = [635e-9] # NOTE must be a list
        self.dx = 3.45e-6 # Pixel width in x-direction
        self.dy = 3.45e-6 # Pixel width in y-direction
        self.crop_fraction = None #Fraction of the image to crop for analysis
        self.rebin_factor = 1 # Rebin the image by factor.  Must be integer
        self.bgd_sub = False
        self.bgd_file = ''
        self.status_msg = ''

    def get_status_msg(self):
        """
        Return the status message
        """
        return self.status_msg

    def load_config(self, filepath):
        """
        Read the config file and load data pertaining to this metadata
        """
        if filepath is None:
            return

        key = 'HOLOGRAM'
        try:
            config = configparser.ConfigParser()
            dataset = config.read(filepath)

            if not dataset:
                raise ValueError("File [%s] doesn't exist."%(filepath))

            wavelength_str = config.get(key, 'wavelength', fallback='405e-9')
            wavelength = [float(w) for w in wavelength_str.split(',')]
            dx = config.getfloat(key, 'dx', fallback=3.45e-6)
            dy = config.getfloat(key, 'dy', fallback=3.45e-6)
            crop_fraction = config.getfloat(key, 'crop_fraction', fallback=0)
            rebin_factor = config.getint(key, 'rebin_factor', fallback=1)
            bgd_sub = config.getboolean(key, 'bgd_sub', fallback=False)

            self.wavelength = wavelength
            self.dx = dx
            self.dy = dy
            self.crop_fraction = crop_fraction
            self.rebin_factor = rebin_factor
            self.bgd_sub = bgd_sub

        except configparser.Error as err:
            print('File read error:  [%s] due to error [%s]. Key=[%s].'\
                  %(filepath, repr(err), key))

class ReconstructionMetadata(MetadataABC):
    """
    Reconstruction Metadata Class
    """
    RECONST_NONE = 0  # Don't compute the reconstruction
    RECONST_AMP = 1  # Compute amplitude only
    RECONST_PHASE = 2  # Compute phase only
    RECONST_INTENSITY = 3  # Compute phase only
    RECONST_AMP_AND_PHASE = 4  # Compute amplitude and phase only
    RECONST_INT_AND_PHASE = 5  # Compute intensity and phase only
    RECONST_ALL = 6  # Compute both everything

    def __init__(self, configfile=None):
        """
        Constructor
        """
        self.propagation_distance = [0.01] #NOTE must be a list

        #must be a list, match same number of values as wavelength
        self.chromatic_shift = [0]

        #True => Compute spectral peak per reconstruction; False => Don't
        #compute spectral peak
        self.compute_spectral_peak = False
        #True => Compute the digital phase mask; False => Don't compute
        #digital phase mask
        self.compute_digital_phase_mask = False

        ### Reference Hologram Parameters
        self.ref_holo = self.ReferenceHologramMetadata()
        ### Phase Mask
        self.phase_mask_reset = False
        ### Phase Unwrapping Parameters
        self.phase_unwrapping = self.PhaseUnwrappingMetadata()
        ### Fitting Parameters
        self.fitting = self.FittingMetadata()
        self.fitting_apply = False
        ### Region Of Interest Parameters
        self.roi_x = self.RoiMetadata()
        self.roi_y = self.RoiMetadata()
        ### Center Image Stuff
        self.center_image = self.CenterImageMetadata()
        self.processing_mode = self.RECONST_NONE
        self.running = False
        #True => store reconstruction data to disk; False => Don't store
        #reconstruction data to disk
        self.store_files = False
        self.status_msg = ''

        self.load_config(configfile)

    def get_status_msg(self):
        """
        Return the status message
        """
        return self.status_msg

    def _processing_mode(self, mode_str):
        """
        Return mode based on string value
        """
        if mode_str.lower() == 'all':
            processing_mode = ReconstructionMetadata.RECONST_ALL
        elif mode_str.lower() == 'amplitude':
            processing_mode = ReconstructionMetadata.RECONST_AMP
        elif mode_str.lower() == 'phase':
            processing_mode = ReconstructionMetadata.RECONST_PHASE
        elif mode_str.lower() == 'intensity':
            processing_mode = ReconstructionMetadata.RECONST_INTENSITY
        elif mode_str.lower() == 'amp_and_phase':
            processing_mode = ReconstructionMetadata.RECONST_AMP_AND_PHASE
        elif mode_str.lower() == 'int_and_phase':
            processing_mode = ReconstructionMetadata.RECONST_INT_AND_PHASE
        else:
            processing_mode = ReconstructionMetadata.RECONST_NONE

        return processing_mode

    def load_config(self, filepath):
        """
        Read the config file and load data pertaining to this metadata
        """
        if filepath is None:
            return

        key = 'RECONSTRUCTION'
        try:
            config = configparser.ConfigParser()
            dataset = config.read(filepath)

            if not dataset:
                raise ValueError("File [%s] doesn't exist."%(filepath))

            propagation_dist_str = config.get(key, 'propagation_distance', fallback='0.01')
            propagation_distance = [float(w) for w in propagation_dist_str.split(',')]
            chromatic_shift_str = config.get(key, 'chromatic_shift', fallback='0')
            chromatic_shift = [float(w) for w in chromatic_shift_str.split(',')]
            compute_spectral_peak = config.getboolean(key,
                                                      'compute_spectral_peak',
                                                      fallback=False)
            compute_digital_phase_mask = config.getboolean(key,
                                                           'compute_digital_phase_mask',
                                                           fallback=False)
            phase_mask_reset = config.getboolean(key, 'phase_mask_reset', fallback=False)
            fitting_apply = config.getboolean(key, 'fitting_apply', fallback=False)
            store_files = config.getboolean(key, 'store_files', fallback=False)
            roi_x_offset = config.getint(key, 'roi_pos_x', fallback=0)
            roi_y_offset = config.getint(key, 'roi_pos_y', fallback=0)
            roi_x_size = config.getint(key, 'roi_size_x', fallback=2048)
            roi_y_size = config.getint(key, 'roi_size_y', fallback=2048)

            mode_str = config.get(key, 'processing_mode', fallback='none')
            processing_mode = self._processing_mode(mode_str)

            self.propagation_distance = propagation_distance
            self.chromatic_shift = chromatic_shift
            self.compute_spectral_peak = compute_spectral_peak
            self.compute_digital_phase_mask = compute_digital_phase_mask
            self.phase_mask_reset = phase_mask_reset
            self.fitting_apply = fitting_apply
            self.store_files = store_files
            self.roi_x.offset = roi_x_offset
            self.roi_y.offset = roi_y_offset
            self.roi_x.size = roi_x_size
            self.roi_y.size = roi_y_size
            self.processing_mode = processing_mode

            self.ref_holo.load_config(filepath)
            self.phase_unwrapping.load_config(filepath)
            self.fitting.load_config(filepath)
            self.center_image.load_config(filepath)

        except configparser.Error as err:
            print('File read error:  [%s] due to error [%s]. Key=[%s].'\
                  %(filepath, repr(err), key))


    class ReferenceHologramMetadata(MetadataABC):
        """
        Reference Hologram Metadata Class
        """
        def __init__(self, path='', enabled=False, averaging_sec=0.0,
                     averaging_enabled=False, save=False):
            """
            Constructor
            """
            self.path = path
            self.enabled = enabled
            self.save = save
            self.averaging_sec = averaging_sec
            self.averaging_enabled = averaging_enabled

        def get_enabled(self):
            """
            Return enabled flag
            """
            return self.enabled

        def load_config(self, filepath):
            """
            Read the config file and load data pertaining to this metadata
            """
            key = 'REFERENCE_HOLOGRAM'

            if filepath is None:
                return

            try:
                config = configparser.ConfigParser()
                dataset = config.read(filepath)

                if not dataset:
                    raise ValueError("File [%s] doesn't exist."%(filepath))

                self.path = config.get(key, 'path', fallback='')
                self.enabled = config.getboolean(key, 'enabled', fallback=False)
                self.save = config.getboolean(key, 'save', fallback=False)
                self.averaging_sec = config.getfloat(key, 'averaging_sec', fallback=0.)
                self.averaging_enabled = config.getboolean(key, 'averaging_enabled', fallback=False)

            except configparser.Error as err:
                print('File read error:  [%s] due to error [%s]. Key=[%s].'\
                      %(filepath, repr(err), key))


    class CenterImageMetadata(MetadataABC):
        """
        Center Image of reconstruction Metadata Class
        """
        def __init__(self, center=False, center_and_tilt=False, max_value=False,
                     wide_spectrum=False, configfile=None):
            """
            Constructor
            """
            self.center = center
            self.center_and_tilt = center_and_tilt
            self.max_value = max_value
            self.wide_spectrum = wide_spectrum

            self.load_config(configfile)

        def get_center(self):
            """
            Return center flag
            """
            return self.center

        def load_config(self, filepath):
            """
            Read the config file and load data pertaining to this metadata
            """
            key = 'CENTER_IMAGE'

            if filepath is None:
                return

            try:

                config = configparser.ConfigParser()
                dataset = config.read(filepath)

                if not dataset:
                    raise ValueError("File [%s] doesn't exist."%(filepath))

                center = config.getboolean(key, 'center', fallback=False)
                center_and_tilt = config.getboolean(key, 'center_and_tilt', fallback=False)
                max_value = config.getboolean(key, 'max_value', fallback=False)
                wide_spectrum = config.getboolean(key, 'wide_spectrum', fallback=False)

                self.center = center
                self.center_and_tilt = center_and_tilt
                self.max_value = max_value
                self.wide_spectrum = wide_spectrum

            except configparser.Error as err:
                print('File read error:  [%s] due to error [%s]. Key=[%s].'\
                      %(filepath, repr(err), key))

    class PhaseUnwrappingMetadata(MetadataABC):
        """
        Phase Unwrapping Metadata Class
        """
        PHASE_UNWRAPPING_NONE = 0
        PHASE_UNWRAPPING_ALG1 = 1
        PHASE_UNWRAPPING_ALG2 = 2

        def __init__(self, enabled=False, algorithm=PHASE_UNWRAPPING_NONE):
            """
            Constructor
            """
            self.enabled = enabled
            self.algorithm = algorithm

        def get_algorithm(self):
            """
            Return algorithm ID
            """
            return self.algorithm

        def load_config(self, filepath):
            """
            Read the config file and load data pertaining to this metadata
            """
            key = 'PHASE_UNWRAPPING'

            if filepath is None:
                return

            try:
                config = configparser.ConfigParser()
                dataset = config.read(filepath)

                if not dataset:
                    raise ValueError("File [%s] doesn't exist."%(filepath))

                enabled = config.getboolean(key, 'enabled', fallback=False)
                algorithm_str = config.get(key, 'algorithm', fallback='none')
                if algorithm_str == 'algorithm_1':
                    algorithm = ReconstructionMetadata.PhaseUnwrappingMetadata.PHASE_UNWRAPPING_ALG1
                elif algorithm_str == 'algorithm_2':
                    algorithm = ReconstructionMetadata.PhaseUnwrappingMetadata.PHASE_UNWRAPPING_ALG2
                else:
                    algorithm = ReconstructionMetadata.PhaseUnwrappingMetadata.PHASE_UNWRAPPING_NONE

                self.enabled = enabled
                self.algorithm = algorithm

            except configparser.Error as err:
                print('File read error:  [%s] due to error [%s]. Key=[%s].'\
                      %(filepath, repr(err), key))

    class FittingMetadata(MetadataABC):
        """
        Fitting Metadata Class
        """
        FITTING_MODE_NONE = 0
        FITTING_MODE_1D_SEGMENT = 1
        FITTING_MODE_2D_SEGMENT = 2
        FITTING_METHOD_NONE = 0
        FITTING_METHOD_POLYNOMIAL = 0

        def __init__(self, mode=FITTING_MODE_NONE, method=FITTING_METHOD_NONE,
                     order=0, applied=False):
            """
            Constructor
            """
            self.mode = mode
            self.method = method
            self.order = order
            self.applied = applied

        def get_mode(self):
            """
            Return Mode
            """
            return self.mode

        def load_config(self, filepath):
            """
            Read the config file and load data pertaining to this metadata
            """

            key = 'FITTING'

            if filepath is None:
                return

            try:
                config = configparser.ConfigParser()
                dataset = config.read(filepath)

                if not dataset:
                    raise ValueError("File [%s] doesn't exist."%(filepath))

                mode_str = config.get(key, 'mode', fallback='')
                if mode_str.lower() == '1d_segment':
                    self.mode = ReconstructionMetadata.FittingMetadata.FITTING_MODE_1D_SEGMENT
                elif mode_str.lower() == '2d_segment':
                    self.mode = ReconstructionMetadata.FittingMetadata.FITTING_MODE_2D_SEGMENT
                else:
                    self.mode = ReconstructionMetadata.FittingMetadata.FITTING_MODE_NONE

                method_str = config.get(key, 'method', fallback='')
                if method_str.lower() == 'polynomial':
                    self.method = ReconstructionMetadata.FittingMetadata.FITTING_METHOD_POLYNOMIAL
                else:
                    self.method = ReconstructionMetadata.FittingMetadata.FITTING_METHOD_NONE

                self.order = config.getint(key, 'order', fallback=0)
                self.applied = config.getboolean(key, 'applied', fallback=False)

            except configparser.Error as err:
                print('File read error:  [%s] due to error [%s]. Key=[%s].'\
                      %(filepath, repr(err), key))

    class RoiMetadata(MetadataABC):
        """
        Region Of Interest Metadata Class
        """
        def __init__(self, offset=0, size=2048):
            """
            Constructor
            """
            self.offset = offset
            self.size = size

        def get_size(self):
            """
            Return size of ROI
            """
            return self.size

        def load_config(self, filepath):
            """
            Read the config file and load data pertaining to this metadata
            """

class ReconstructionDoneMetadata(MetadataABC):
    """
    Reconstruction Done Metadata Class
    """
    def __init__(self, done=True):
        """
        Constructor
        """
        self.done = done

    def get_done(self):
        """
        Return the done flag
        """
        return self.done

    def load_config(self, filepath):
        """
        Read the config file and load data pertaining to this metadata
        """


class FouriermaskMetadata(MetadataABC):
    """
    Fourier Mask Metadata Class
    """
    def __init__(self):
        """
        Constructor
        """
        self.center_list = []
        self.mask = None
        self.status_msg = ""

    def get_status_msg(self):
        """
        Return the status message
        """
        return self.status_msg

    def load_config(self, filepath):
        """
        Read the config file and load data pertaining to this metadata
        """
        key = 'FOURIERMASK'
        if filepath is None:
            return

        try:
            config = configparser.ConfigParser()
            dataset = config.read(filepath)

            if not dataset:
                raise ValueError("File [%s] doesn't exist."%(filepath))

            center_x_str = config.get(key, 'center_x', fallback='702, 1117, 1439')
            center_x = [float(c) for c in center_x_str.split(',')]
            center_y_str = config.get(key, 'center_y', fallback='749, 6161, 893')
            center_y = [float(c) for c in center_y_str.split(',')]
            radius_str = config.get(key, 'radius', fallback='170, 170, 170')
            radius = [float(c) for c in radius_str.split(',')]

            wavelength_str = config.get('HOLOGRAM', 'wavelength', fallback='405e-9')
            wavelength = [float(w) for w in wavelength_str.split(',')]
            N = config.getint('CAMERA', 'N', fallback=2048)

            self.center_list = []
            for i in range(len(wavelength)):
                self.center_list.append(Circle(center_x[i], center_y[i], radius[i]))

            self.mask = Mask(N, self.center_list[0:len(wavelength)])

        except configparser.Error as err:
            print('File read error:  [%s] due to error [%s]. Key=[%s].'\
                  %(filepath, repr(err), key))

class SessionMetadata(MetadataABC):
    """
    Session Metadata Class
    """
    def __init__(self):
        self.name = ""
        self.description = ""
        self.holo = HologramMetadata()
        self.lens = self.LensMetadata()
        self.status_msg = ""

    def get_status_msg(self):
        """
        Return the status message
        """
        return self.status_msg

    def load_config(self, filepath):
        """
        Read the config file and load data pertaining to this metadata
        """
        key = 'SESSION'
        if filepath is None:
            return

        try:
            config = configparser.ConfigParser()
            dataset = config.read(filepath)

            if not dataset:
                raise ValueError("File [%s] doesn't exist."%(filepath))

            self.name = config.get(key, 'name', fallback='')
            self.description = config.get(key, 'description', fallback='')
            self.holo.load_config(filepath)
            self.lens.load_config(filepath)

        except configparser.Error as err:
            print('File read error:  [%s] due to error [%s]. Key=[%s].'\
                  %(filepath, repr(err), key))

    class LensMetadata(MetadataABC):
        """
        Lens Metadata
        """
        def __init__(self):
            """
            Constructor
            """
            self.focal_length = 1e-3 #mm
            self.numerical_aperture = 0.1
            self.system_magnification = 1.0
            self.reconst_space = False #False==>Object space; True==>Detector space

        def get_focal_length(self):
            """
            Return the status message
            """
            return self.focal_length

        def load_config(self, filepath):
            """
            Read the config file and load data pertaining to this metadata
            """
            key = 'LENS'

            if filepath is None:
                return

            try:
                config = configparser.ConfigParser()
                dataset = config.read(filepath)

                if not dataset:
                    raise ValueError("File [%s] doesn't exist."%(filepath))

                focal_length = config.getfloat(key, 'focal_length', fallback=1e-3)
                numerical_aperture = config.getfloat(key, 'numerical_aperture', fallback=0.1)
                system_magnification = config.getfloat(key, 'system_magnification', fallback=1.0)
                reconst_space = config.getfloat(key, 'reconst_space', fallback=False)

                self.focal_length = focal_length
                self.numerical_aperture = numerical_aperture
                self.system_magnification = system_magnification
                self.reconst_space = reconst_space

            except configparser.Error as err:
                print('File read error:  [%s] due to error [%s]. Key=[%s].'\
                      %(filepath, repr(err), key))

if __name__ == "__main__":

    FNAME = 'DEFAULT.ini'
    MetadataDictionary(FNAME)

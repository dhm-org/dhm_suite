import time
import configparser
from shampoo.mask import (Circle, Mask)

class Metadata_Object(object):
    pass

class Metadata_Dictionary(object):

    def __init__(self, configfile=None):
        self.metadata = {}
        self.metadata['CONTROLLER'] = Controller_Metadata()
        self.metadata['HEARTBEAT'] = Heartbeat_Metadata()
        self.metadata['GUISERVER'] = Guiserver_Metadata()
        self.metadata['DATALOGGER'] = Datalogger_Metadata()
        self.metadata['CAMERA'] = Camera_Metadata()
        self.metadata['FRAMESOURCE'] = Framesource_Metadata()
        self.metadata['WATCHDOG'] = Watchdog_Metadata()
        self.metadata['HOLOGRAM'] = Hologram_Metadata()
        self.metadata['RECONSTRUCTION'] = Reconstruction_Metadata()
        self.metadata['FOURIERMASK'] = Fouriermask_Metadata()
        self.metadata['SESSION'] = Session_Metadata()

        for k in self.metadata.keys():
            self.metadata[k].load_config(configfile)

class Controller_Metadata(Metadata_Object):
    def __init__(self, configfile=None, cmd_hostname='localhost', cmd_port=10000):

        self.cmd_hostname= cmd_hostname
        self.cmd_port = cmd_port
        
        self.load_config(configfile)

    def load_config(self, filepath):
        if filepath is None:
            return

        key = 'CONTROLLER'
        try:
            config = configparser.ConfigParser()
            config.read(filepath)
    
            cmd_hostname = config.get(key,'cmd_hostname',fallback='localhost')
            cmd_port = config.getint(key,'cmd_port',fallback=10000)

            self.cmd_hostname = cmd_hostname
            self.cmd_port = cmd_port

        except configparser.Error as e:
            print('Unable to read config file [%s] due to error [%s].'%(filepath, repr(e)))

class Heartbeat_Metadata(Metadata_Object):
    def __init__(self):
        self.ident = ''
        self.timestamp = time.time()
        self.exception = None

    def load_config(self, filepath):
        pass
        
class Guiserver_Metadata(Metadata_Object):
    def __init__(self, configfile=None):

        self.connection_status= [False, False, False, False, False, False]
        self.enabled = {'rawframes':True, 'fourier':True, 'reconst_amp':True, 'reconst_intensity':True, 'reconst_phase':True}
        self.ports = {'fourier':9993, 'reconst_amp':9994, 'raw_frames':9995, 'telemetry':9996, 'reconst_intensity':9997, 'reconst_phase':9998}
        self.hostname = '127.0.0.1'
        self.maxclients = 5
        self.status_msg = ''

        self.load_config(configfile)

    def load_config(self, filepath):

        if filepath is None:
            return

        key = 'GUISERVER'
        try:
            config = configparser.ConfigParser()
            config.read(filepath)
    
            fourier_port = config.getint(key,'fourier_port',fallback=9993)
            reconst_amp_port = config.getint(key,'reconst_amp_port',fallback=9994)   
            raw_frames_port = config.getint(key,'raw_frames_port',fallback=9995)   
            telemetry_port = config.getint(key,'telemetry_port',fallback=9996)   
            reconst_intensity_port = config.getint(key,'reconst_intensity_port',fallback=9997)
            reconst_phase_port = config.getint(key,'reconst_phase_port',fallback=9998)
            host = config.get(key,'host',fallback='127.0.0.1')   
            maxclients = config.getint(key,'maxclients',fallback=5)

            self.ports['fourier'] = fourier_port
            self.ports['reconst_amp'] = reconst_amp_port
            self.ports['raw_frames'] = raw_frames_port
            self.ports['telemetry'] = telemetry_port
            self.ports['reconst_intensity'] = reconst_intensity_port
            self.ports['reconst_phase'] = reconst_phase_port
            self.hostname = host
            self.maxclients = maxclients

        except configparser.Error as e:
            print('Unable to read config file [%s] due to error [%s].'%(filepath, repr(e)))

        

class Datalogger_Metadata(Metadata_Object):
    def __init__(self, configfile=None):
        self.enabled = True
        self.status_msg = ''

        self.load_config(configfile)

    def load_config(self, filepath):

        key = 'DATALOGGER'
        if filepath is None:
            return

        try:
            config = configparser.ConfigParser()
            config.read(filepath)
    
            enabled = config.getboolean(key,'enabled',fallback=False)
            self.enabled = enabled

        except configparser.Error as e:
            print('Unable to read config file [%s] due to error [%s].'%(filepath, repr(e), key))

class Camera_Metadata(Metadata_Object):
    def __init__(self, N=2048, rate=15.0, shutter=15000, gain=0, roi_pos=(0,0), roi_size=(2048,2048)):
        self.N = N
        self.rate = rate
        self.shutter = shutter
        self.gain = gain
        self.roi_pos = roi_pos
        self.roi_size = roi_size
        self.status_msg = ''

    def load_config(self, filepath):

        key = 'CAMERA'
        if filepath is None:
            return

        try:
            config = configparser.ConfigParser()
            config.read(filepath)
    
            N = config.getint(key,'N',fallback=2048)
            rate = config.getfloat(key,'rate',fallback=15.0)
            shutter = config.getint(key,'shutter',fallback=15000)
            gain = config.getint(key,'gain',fallback=0)
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

        except configparser.Error as e:
            print('Unable to read config file [%s] due to error [%s].'%(filepath, repr(e), key))

class Camera_Server_Metadata(Metadata_Object):
    def __init__(self, configfile=None):
        self.host = '127.0.0.1'
        BASE_PORT = 2000
        self.ports = {'frame':BASE_PORT, 'command':BASE_PORT+1, 'telemetry':BASE_PORT+2}
        self.status_msg = ''

        self.load_config(configfile)

    def load_config(self, filepath):
        if filepath is None:
            return

        key = 'CAMERA_SERVER'
        try:
            config = configparser.ConfigParser()
            config.read(filepath)
            host = config.get(key,'host',fallback='127.0.0.1')   
            frame_port = config.getint(key,'frame',fallback=2000)   
            command_port = config.getint(key,'command',fallback=2001)
            telemetry_port = config.getint(key,'telemetry',fallback=2002)

            self.host = host
            self.ports['frame'] = frame_port
            self.ports['command'] = command_port
            self.ports['telemetry'] = telemetry_port

        except configparser.Error as e:
            print('Unable to read config file [%s] due to error [%s].  Key=[%s].'%(filepath, repr(e), key))

class Framesource_Metadata(Metadata_Object):
    FRAMESOURCE_FILE  = 0  # Don't compute the reconstruction
    FRAMESOURCE_MICROSCOPE  = 1  # Don't compute the reconstruction

    FRAMESOURCE_STATE_IDLE = 0
    FRAMESOURCE_STATE_RUNNING = 1

    def __init__(self, configfile=None):
        self.state = self.FRAMESOURCE_STATE_IDLE
        self.mode = ''
        self.camserver = Camera_Server_Metadata(configfile=configfile)
        self.file = {}
        self.file['datadir'] = '/proj/dhm/sfregoso/git_repos/dhmsw/simulated_frames/*.bmp'
        self.file['currentfile'] = '/proj/dhm/sfregoso/git_repos/dhmsw/simulated_frames/*.bmp'
        self.status_msg = ''

        self.load_config(configfile)

    def load_config(self, filepath):
        if filepath is None:
            return

        key = 'FRAMESOURCE'
        try:
            config = configparser.ConfigParser()
            config.read(filepath)
            datadir = config.get(key,'datadir',fallback='')   
            self.datadir = datadir

        except configparser.Error as e:
            print('Unable to read config file [%s] due to error [%s].  Key=[%s].'%(filepath, repr(e), key))

class Watchdog_Metadata(object):
    def __init__(self):
        self.status_msg = ''
        pass
    def load_config(self, filepath):
        pass

class Hologram_Metadata(Metadata_Object):
    def __init__(self):
        self.wavelength = [635e-9] # NOTE must be a list
        self.dx = 3.45e-6 # Pixel width in x-direction
        self.dy = 3.45e-6 # Pixel width in y-direction
        self.crop_fraction = None #Fraction of the image to crop for analysis
        self.rebin_factor = 1 # Rebin the image by factor.  Must be integer
        self.bgd_sub = False
        self.bgd_file = ''
        self.status_msg = ''

    def load_config(self, filepath):
        if filepath is None:
            return

        key = 'HOLOGRAM'
        try:
            config = configparser.ConfigParser()
            config.read(filepath)
            wavelength_str = config.get(key,'wavelength',fallback='405e-9')   
            wavelength = [float(w) for w in wavelength_str.split(',')]
            dx = config.getfloat(key,'dx',fallback=3.45e-6)   
            dy = config.getfloat(key,'dy',fallback=3.45e-6)   
            crop_fraction = config.getfloat(key,'crop_fraction',fallback=0)   
            rebin_factor = config.getint(key,'rebin_factor',fallback=1)   
            bgd_sub = config.getboolean(key,'bgd_sub',fallback=False)   

            self.wavelength = wavelength
            self.dx = dx
            self.dy = dy
            self.crop_fraction = crop_fraction
            self.rebin_factor = rebin_factor
            self.bgd_sub = bgd_sub

        except configparser.Error as e:
            print('Unable to read config file [%s] due to error [%s].  Key=[%s].'%(filepath, repr(e), key))

class Reconstruction_Metadata(Metadata_Object):
    RECONST_NONE  = 0  # Don't compute the reconstruction
    RECONST_AMP   = 1  # Compute amplitude only
    RECONST_PHASE = 2  # Compute phase only
    RECONST_INTENSITY = 3  # Compute phase only
    RECONST_AMP_AND_PHASE = 4  # Compute amplitude and phase only
    RECONST_INT_AND_PHASE = 5  # Compute intensity and phase only
    RECONST_ALL   = 6  # Compute both everything
    
    def __init__(self, configfile=None):
        self.propagation_distance = [0.01] #NOTE must be a list
        self.chromatic_shift = [0] #must be a list, match same number of values as wavelength
        self.compute_spectral_peak = False #True => Compute spectral peak per reconstruction; False => Don't compute spectral peak
        self.compute_digital_phase_mask = False #True => Compute the digital phase mask; False => Don't compute digital phase mask
        ### Reference Hologram Parameters
        self.ref_holo = self.ReferenceHologram_Metadata()
        ### Phase Mask
        self.phase_mask_reset = False
        ### Phase Unwrapping Parameters
        self.phase_unwrapping = self.PhaseUnwrapping_Metadata()
        ### Fitting Parameters
        self.fitting = self.Fitting_Metadata()
        self.fitting_apply = False
        ### Region Of Interest Parameters
        self.roi_x = self.Roi_Metadata()
        self.roi_y = self.Roi_Metadata()
        ### Center Image Stuff
        self.center_image = self.CenterImage_Metadata()
        self.processing_mode = self.RECONST_NONE
        self.running = False
        self.store_files = False #True => store reconstruction data to disk; False => Don't store reconstruction data to disk
        self.status_msg = ''

        self.load_config(configfile)

    def load_config(self, filepath):
        if filepath is None:
            return

        key = 'RECONSTRUCTION'
        try:
            config = configparser.ConfigParser()
            config.read(filepath)

            propagation_dist_str = config.get(key, 'propagation_distance', fallback='0.01')
            propagation_distance= [float(w) for w in propagation_dist_str.split(',')]
            chromatic_shift_str = config.get(key, 'chromatic_shift', fallback='0')
            chromatic_shift= [float(w) for w in chromatic_shift_str.split(',')]
            compute_spectral_peak = config.getboolean(key, 'compute_spectral_peak', fallback=False)
            compute_digital_phase_mask = config.getboolean(key, 'compute_digital_phase_mask', fallback=False)
            phase_mask_reset = config.getboolean(key, 'phase_mask_reset', fallback=False)
            fitting_apply = config.getboolean(key, 'fitting_apply', fallback=False)
            store_files = config.getboolean(key, 'store_files', fallback=False)
            roi_x_offset = config.getint(key, 'roi_pos_x', fallback=0)
            roi_y_offset = config.getint(key, 'roi_pos_y', fallback=0)
            roi_x_size = config.getint(key, 'roi_size_x', fallback=2048)
            roi_y_size = config.getint(key, 'roi_size_y', fallback=2048)
            processing_mode_str = config.get(key, 'processing_mode', fallback='none')
            if processing_mode_str.lower() == 'all':
                processing_mode = Reconstruction_Metadata.RECONST_ALL;
            elif processing_mode_str.lower() == 'amplitude':
                processing_mode = Reconstruction_Metadata.RECONST_AMP;
            elif processing_mode_str.lower() == 'phase':
                processing_mode = Reconstruction_Metadata.RECONST_PHASE;
            elif processing_mode_str.lower() == 'intensity':
                processing_mode = Reconstruction_Metadata.RECONST_INTENSITY;
            elif processing_mode_str.lower() == 'amp_and_phase':
                processing_mode = Reconstruction_Metadata.RECONST_AMP_AND_PHASE;
            elif processing_mode_str.lower() == 'int_and_phase':
                processing_mode = Reconstruction_Metadata.RECONST_INT_AND_PHASE;
            else:
                processing_mode = Reconstruction_Metadata.RECONST_NONE;

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

        except configparser.Error as e:
            print('Unable to read config file [%s] due to error [%s].  Key=[%s].'%(filepath, repr(e), key))


    class ReferenceHologram_Metadata(Metadata_Object):
        def __init__(self, path='', enabled=False, averaging_sec=0.0, averaging_enabled=False, save=False):
            self.path = path
            self.enabled = enabled
            self.save = save
            self.averaging_sec = averaging_sec
            self.averaging_enabled = averaging_enabled

        def load_config(self, filepath):
            key = 'REFERENCE_HOLOGRAM'

            if filepath is None:
                return

            try:
                config = configparser.ConfigParser()
                config.read(filepath)

                path = config.get(key, 'path', fallback='')
                enabled = config.getboolean(key, 'enabled', fallback=False)
                save= config.getboolean(key, 'save', fallback=False)
                averaging_sec = config.getfloat(key, 'averaging_sec', fallback=0.)
                averaging_enabled = config.getboolean(key, 'averaging_enabled', fallback=False)

                self.path = config.get(key, 'path', fallback='')
                self.enabled = config.getboolean(key, 'enabled', fallback=False)
                self.save= config.getboolean(key, 'save', fallback=False)
                self.averaging_sec = config.getfloat(key, 'averaging_sec', fallback=0.)
                averaging_enabled = config.getboolean(key, 'averaging_enabled', fallback=False)

            except configparser.Error as e:
                print('Unable to read config file [%s] due to error [%s].  Key=[%s].'%(filepath, repr(e), key))


    class CenterImage_Metadata(Metadata_Object):
        def __init__(self, center=False, center_and_tilt=False, max_value=False, wide_spectrum=False, configfile=None):
            self.center = center
            self.center_and_tilt = center_and_tilt
            self.max_value = max_value
            self.wide_spectrum = wide_spectrum
 
            self.load_config(configfile)

        def load_config(self, filepath):
            key = 'CENTER_IMAGE'

            if filepath is None:
                return

            try:

                config = configparser.ConfigParser()
                config.read(filepath)

                center = config.getboolean(key, 'center', fallback=False)
                center_and_tilt = config.getboolean(key, 'center_and_tilt', fallback=False)
                max_value = config.getboolean(key, 'max_value', fallback=False)
                wide_spectrum = config.getboolean(key, 'wide_spectrum', fallback=False)
                
                self.center = center
                self.center_and_tilt = center_and_tilt
                self.max_value = max_value
                self.wide_spectrum = wide_spectrum

            except configparser.Error as e:
                print('Unable to read config file [%s] due to error [%s].  Key=[%s].'%(filepath, repr(e), key))

    class PhaseUnwrapping_Metadata(Metadata_Object):
        PHASE_UNWRAPPING_NONE = 0
        PHASE_UNWRAPPING_ALG1 = 1
        PHASE_UNWRAPPING_ALG2 = 2
        def __init__(self, enabled=False, algorithm=PHASE_UNWRAPPING_NONE):
            self.enabled = enabled
            self.algorithm = algorithm

        def load_config(self, filepath):
            key = 'PHASE_UNWRAPPING'

            if filepath is None:
                return

            try:
                config = configparser.ConfigParser()
                config.read(filepath)

                enabled = config.getboolean(key, 'enabled', fallback=False)
                algorithm_str = config.get(key, 'algorithm', fallback='none')
                if algorithm_str == 'algorithm_1':
                    algorithm = Reconstruction_Metadata.PhaseUnwrapping_Metadata.PHASE_UNWRAPPING_ALG1
                elif algorithm_str == 'algorithm_2':
                    algorithm = Reconstruction_Metadata.PhaseUnwrapping_Metadata.PHASE_UNWRAPPING_ALG2
                else:
                    algorithm = Reconstruction_Metadata.PhaseUnwrapping_Metadata.PHASE_UNWRAPPING_NONE

                self.enabled = enabled
                self.algorithm = algorithm

            except configparser.Error as e:
                print('Unable to read config file [%s] due to error [%s].  Key=[%s].'%(filepath, repr(e), key))

    class Fitting_Metadata(Metadata_Object):
        FITTING_MODE_NONE = 0
        FITTING_MODE_1D_SEGMENT = 1
        FITTING_MODE_2D_SEGMENT = 2
        FITTING_METHOD_NONE = 0
        FITTING_METHOD_POLYNOMIAL = 0

        def __init__(self, mode=FITTING_MODE_NONE, method=FITTING_METHOD_NONE, order=0, applied=False):
            self.mode = mode
            self.method = method
            self.order = order
            self.applied = applied

        def load_config(self, filepath):

            key = 'FITTING'

            if filepath is None:
                return

            try:
                config = configparser.ConfigParser()
                config.read(filepath)

                mode_str = config.get(key, 'mode', fallback='')
                if mode_str.lower() == '1d_segment':
                    self.mode = Reconstruction_Metadata.Fitting_Metadata.FITTING_MODE_1D_SEGMENT
                elif mode_str.lower() == '2d_segment':
                    self.mode = Reconstruction_Metadata.Fitting_Metadata.FITTING_MODE_2D_SEGMENT
                else:
                    self.mode = Reconstruction_Metadata.Fitting_Metadata.FITTING_MODE_NONE
            
                method_str = config.get(key, 'method', fallback='')
                if method_str.lower() == 'polynomial':
                    self.method = Reconstruction_Metadata.Fitting_Metadata.FITTING_METHOD_POLYNOMIAL
                else:
                    self.method = Reconstruction_Metadata.Fitting_Metadata.FITTING_METHOD_NONE
            
                self.order = config.getint(key, 'order', fallback=0)
                self.applied = config.getboolean(key, 'applied', fallback=False)

            except configparser.Error as e:
                print('Unable to read config file [%s] due to error [%s].  Key=[%s].'%(filepath, repr(e), key))

    class Roi_Metadata(Metadata_Object):
        def __init__(self, offset=0, size=2048):
            self.offset = offset
            self.size = size

class Reconstruction_Done_Metadata(Metadata_Object):
    def __init__(self, done=True):
        self.done = done
      

class Fouriermask_Metadata(Metadata_Object):
    def __init__(self):
        self.center_list = []
        self.mask = None
        self.status_msg = ""

    def load_config(self, filepath):
        key = 'FOURIERMASK'
        if filepath is None:
            return

        try:
            config = configparser.ConfigParser()
            config.read(filepath)

            center_x_str = config.get(key, 'center_x', fallback='702, 1117, 1439')
            center_x = [float(c) for c in center_x_str.split(',')]
            center_y_str = config.get(key, 'center_y', fallback='749, 6161, 893')
            center_y = [float(c) for c in center_y_str.split(',')]
            radius_str = config.get(key, 'radius', fallback='170, 170, 170')
            radius = [float(c) for c in radius_str.split(',')]

            wavelength_str = config.get('HOLOGRAM','wavelength',fallback='405e-9')   
            wavelength = [float(w) for w in wavelength_str.split(',')]
            N = config.getint('CAMERA','N',fallback=2048)   

            self.center_list = []
            for i in range(len(wavelength)):
                self.center_list.append( Circle(center_x[i], center_y[i], radius[i]) )

            self.mask = Mask(N, self.center_list[0:len(wavelength)])

        except configparser.Error as e:
            print('Unable to read config file [%s] due to error [%s].  Key=[%s].'%(filepath, repr(e), key))

class Session_Metadata(Metadata_Object):
    def __init__(self):
        self.name = ""
        self.description = ""
        self.holo = Hologram_Metadata()
        self.lens = self.Lens_Metadata()
        self.status_msg = ""

    def load_config(self, filepath):
        key = 'SESSION'
        if filepath is None:
            return

        try:
            config = configparser.ConfigParser()
            config.read(filepath)

            self.name = config.get(key, 'name', fallback='')
            self.description = config.get(key, 'description', fallback='')
            self.holo.load_config(filepath)
            self.lens.load_config(filepath)

        except configparser.Error as e:
            print('Unable to read config file [%s] due to error [%s].  Key=[%s].'%(filepath, repr(e), key))

    class Lens_Metadata(Metadata_Object):

        def __init__(self):
            self.focal_length = 1e-3 #mm
            self.numerical_aperture = 0.1
            self.system_magnification = 1.0

        def load_config(self, filepath):
            key = 'LENS'

            if filepath is None:
                return 

            try:
                config = configparser.ConfigParser()
                config.read(filepath)

                focal_length = config.getfloat(key, 'focal_length', fallback=1e-3)
                numerical_aperture = config.getfloat(key, 'numerical_aperture', fallback=0.1)
                system_magnification = config.getfloat(key, 'system_magnification', fallback=1.0)

                self.focal_length = focal_length
                self.numerical_aperture = numerical_aperture
                self.system_magnification = system_magnification

            except configparser.Error as e:
                print('Unable to read config file [%s] due to error [%s].  Key=[%s].'%(filepath, repr(e), key))

if __name__ == "__main__":
    fname = 'DEFAULT.ini'
    meta = Metadata_Dictionary(fname)



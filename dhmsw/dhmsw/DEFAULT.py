import numpy as np
import socket
import metadata_classes
from shampoo.mask import (Circle, Mask)

###############################################################################
### GUI Server Settings
###############################################################################
GUI_SERVER_BASE_PORT = 9993
guiserver_meta = metadata_classes.Guiserver_Metadata()
guiserver_meta.ports['fourier']           = GUI_SERVER_BASE_PORT
guiserver_meta.ports['reconst_amp']       = GUI_SERVER_BASE_PORT + 1
guiserver_meta.ports['raw_frames']        = GUI_SERVER_BASE_PORT + 2
guiserver_meta.ports['telemetry']         = GUI_SERVER_BASE_PORT + 3
guiserver_meta.ports['reconst_intensity'] = GUI_SERVER_BASE_PORT + 4
guiserver_meta.ports['reconst_phase']     = GUI_SERVER_BASE_PORT + 5
guiserver_meta.hostname   = socket.gethostname()
guiserver_meta.maxclients = 5

###############################################################################
### Data Logger Parameters
###############################################################################
datalogger_meta = metadata_classes.Datalogger_Metadata()

###############################################################################
### Camera Parameters
###############################################################################
camera_meta          = metadata_classes.Camera_Metadata()
camera_meta.N        = 2048 # image size
camera_meta.rate     = 15.
camera_meta.exposure_time = 15000
camera_meta.gain     = 0
camera_meta.roi_pos  = (0, 0) #(x, y)
camera_meta.roi_size = (camera_meta.N, camera_meta.N) #x_size, y_size

###############################################################################
### Hologram parameters
###############################################################################
holo_meta               = metadata_classes.Hologram_Metadata()
holo_meta.wavelength    = [405e-9] #[405e-9, 488e-9, 532e-9] # NOTE must be a list
holo_meta.dx            = 3.45e-6 # Pixel width in x-direction
holo_meta.dy            = 3.45e-6 # Pixel width in y-direction
holo_meta.crop_fraction = 0 #Fraction of the image to crop for analysis
holo_meta.rebin_factor  = 1 # Rebin the image by factor.  Must be integer
holo_meta.bgd_sub       = False
holo_meta.bgd_file      = ''

###############################################################################
### Reconstruction Parameters
###############################################################################
reconst_meta = metadata_classes.Reconstruction_Metadata()
reconst_meta.propagation_distance = [0.01] #[0.01, 0.01, 0.01] #NOTE must be a list
reconst_meta.chromatic_shift = [0] * len(holo_meta.wavelength)
reconst_meta.compute_spectral_peak = False
reconst_meta.compute_digital_phase_mask = False
reconst_meta.processing_mode = metadata_classes.Reconstruction_Metadata.RECONST_NONE

#################################################################################
### Session Parameters
#################################################################################
session_meta = metadata_classes.Session_Metadata()
#session_meta.name = 'Default Session'
#session_meta.description = ''
session_meta.holo = holo_meta
session_meta.lens = metadata_classes.Session_Metadata.Lens_Metadata()
session_meta.lens.focal_length = 1e-3 #mm
session_meta.lens.numerical_aperture = 0
session_meta.lens.system_magnification = 0
session_meta.status_msg=""

#################################################################################
### Fourier Mask Parameters
#################################################################################
fouriermask_meta = metadata_classes.Fouriermask_Metadata()
#centerx, centery, radius = (1485, 1496, 200) ### NOTE:  For simulated file
#center_list.append( Circle(centerx, centery, radius) )
#centerx, centery, radius = (1206, 616, 170)
#center_list.append( Circle(centerx, centery, radius) )
#centerx, centery, radius = (1472, 976, 170)
#center_list.append( Circle(centerx, centery, radius) )
centerx, centery, radius = (702, 749, 170)
fouriermask_meta.center_list.append( Circle(centerx, centery, radius) )
centerx, centery, radius = (1117, 616, 170)
fouriermask_meta.center_list.append( Circle(centerx, centery, radius) )
centerx, centery, radius = (1439, 893, 170)
fouriermask_meta.center_list.append( Circle(centerx, centery, radius) )
fouriermask_meta.mask = Mask(camera_meta.N, fouriermask_meta.center_list[0:len(holo_meta.wavelength)])

###############################################################################
###  Framesource Parameters
###############################################################################
framesource_meta = metadata_classes.Framesource_Metadata()
framesource_meta.file['datadir'] = '../tests/simulated_frames/*.bmp'


###############################################################################
###  Watchdog Parameters
###############################################################################
watchdog_meta = metadata_classes.Watchdog_Metadata()


import sys
import time
import ntpath
from shampoo_lite.reconstruction import (Hologram)
import numpy as np
from skimage.io import imread
import matplotlib.pyplot as plt

PLOT = True

#path = './data/USAF_multi.tif'
#wl = [405e-3, 532e-3, 650e-3] #um
#propagation_dist = [65, 260, 360] #um
#chromatic_shift = [0, 0, 0] #um
#magnification = 10 #magnification of the system
#p = 3.45 # um pixel (image space)
#center_x=[1267, 1599, 1382]
#center_y=[1483, 1042, 440]
#radius=[250, 250, 250]

path = '/Users/sfregoso/Documents/old_mac/MacPro_2012thru2015/Santos/Work/FelipeStuff/DHM/reconstruction_comparison/lilipond_data/Numerical_Reconstruction_Example/Lily_Pond_Data/2020.02.28_17.13.10.880/Holograms/00100_holo.tif'
wl = [405e-3] #um
propagation_dist = [710, 380] #um
chromatic_shift = None #um
magnification = 10 #magnification of the system
p = 2.2 # um pixel (image space)
center_x=[1716]
center_y=[836]
radius=[310]

# Read image file and return numpy array
im = imread(path)

# Create hologram object
holo = Hologram(im, wavelength = wl, pix_dx=p, pix_dy=p, system_magnification=magnification)

# Create the Fourier mask based on center positions and radius
fourier_mask = holo.generate_spectral_mask(center_x=center_x, center_y=center_y, radius=radius)

for prop_dist in propagation_dist:

    # Create propagation kernel based on propagation distance
    G_factor = holo.generate_propagation_kernel(prop_dist, fourier_mask.mask_centered)

    start_time = time.time()
    w = holo.reconstruct(prop_dist, fourier_mask=fourier_mask, G_factor=G_factor, chromatic_shift=chromatic_shift)
    print("Elapsed Time:  ", time.time()-start_time)

    w.amplitude
    w.phase

    w.save_to_file('/Users/sfregoso/Documents/old_mac/MacPro_2012thru2015/Santos/Work/FelipeStuff/DHM/git_repos/dhm_suite/shampoo_lite/Reconstructions/')
    amp_name = "amplitude_Z%g_"%(prop_dist) + ntpath.basename(path)
    plt.imsave(amp_name, w.amplitude[:,:,0,0], format='tiff')

    phase_name = "phase_Z%g_"%(prop_dist) + ntpath.basename(path)
    plt.imsave(phase_name, w.phase[:,:,0,0], format='tiff')

if PLOT:
    f, axes = plt.subplots(1, 3, sharex=True)
    axes[0].imshow(w.amplitude[:,:,0,0])
    #axes[1].imshow(w.amplitude[:,:,0,1])
    #axes[2].imshow(w.amplitude[:,:,0,2])

    
    f, axes = plt.subplots(1, 3, sharex=True)
    wv = 0
    axes[0].imshow(w.phase[:,:,0,0])
    #axes[1].imshow(w.phase[:,:,0,1])
    #axes[2].imshow(w.phase[:,:,0,2])


plt.show()

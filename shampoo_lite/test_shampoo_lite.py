import sys
import time
from shampoo_lite.reconstruction import (Hologram)
import numpy as np
from skimage.io import imread
import matplotlib.pyplot as plt

path = './data/USAF_multi.tif'

im = imread(path)

wl = [405e-3, 532e-3, 650e-3] #um
propagation_dist = [65, 260, 360] #um
chromatic_shift = [0, 0, 0] #um
magnification = 10 #magnification of the system
p = 3.45 # um pixel (image space)

holo = Hologram(im, wavelength = wl, pix_dx=p, pix_dy=p, system_magnification=magnification)

print("dk = ", holo.dk)

ft_hologram = holo.ft_hologram

print(type(ft_hologram))

fourier_mask = holo.generate_spectral_mask(center_x=[1267, 1599, 1382], center_y=[1483, 1042, 440], radius=[250, 250, 250])
print(type(fourier_mask))
print(type(holo))
print(propagation_dist[0])
G_factor = holo.generate_propagation_kernel(propagation_dist[0], fourier_mask.mask_centered)

start_time = time.time()
w = holo.reconstruct(propagation_dist[0], compute_spectral_peak=False, fourier_mask=fourier_mask, G_factor=G_factor)
print("Elapsed Time:  ", time.time()-start_time)

start_time = time.time()
w = holo.reconstruct(propagation_dist[0], compute_spectral_peak=False, fourier_mask=fourier_mask, G_factor=G_factor)
print("Elapsed Time:  ", time.time()-start_time)

print(w.amplitude.shape)
#f, axes = plt.subplots(1, 1, sharex=True)
#wv = 0 
#axes.imshow(np.log(np.abs(holo.ft_hologram)).astype(np.uint8))

#f, axes = plt.subplots(1, 1, sharex=True)
#wv = 0
#axes.imshow(w.intensity[:,:,0,wv])

f, axes = plt.subplots(1, 3, sharex=True)
axes[0].imshow(w.amplitude[:,:,0,0])
axes[1].imshow(w.amplitude[:,:,0,1])
axes[2].imshow(w.amplitude[:,:,0,2])

f, axes = plt.subplots(1, 3, sharex=True)
wv = 0
axes[0].imshow(w.phase[:,:,0,0])
axes[1].imshow(w.phase[:,:,0,1])
axes[2].imshow(w.phase[:,:,0,2])

plt.show()

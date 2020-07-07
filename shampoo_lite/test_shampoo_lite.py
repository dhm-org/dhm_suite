import sys
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

holo = Hologram(im, wavelength = wl[0], pix_dx=p, pix_dy=p, system_magnification=magnification)

ft_hologram = holo.ft_hologram

print(type(ft_hologram))

holo.spectral_peak

w = holo.reconstruct(propagation_dist[0], compute_spectral_peak=True)

#f, axes = plt.subplots(1, 1, sharex=True)
#wv = 0 
#axes.imshow(np.log(np.abs(holo.ft_hologram)).astype(np.uint8))

#f, axes = plt.subplots(1, 1, sharex=True)
#wv = 0
#axes.imshow(w.intensity[:,:,0,wv])

f, axes = plt.subplots(1, 1, sharex=True)
wv = 0
axes.imshow(w.amplitude[:,:,0,wv])

f, axes = plt.subplots(1, 1, sharex=True)
wv = 0
axes.imshow(w.phase[:,:,0,wv])

plt.show()

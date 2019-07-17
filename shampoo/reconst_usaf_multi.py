import sys
from shampoo.reconstruction import (Hologram, Mask)
from skimage.io import imread
import matplotlib.pyplot as plt
import numpy as np
import os

###############################################################################
###  Read file
###############################################################################
path = os.path.dirname(os.path.abspath(__file__)) + '/data/USAF_multi.tif'
#path = '/proj/dhm/sfregoso/git_repos/dhmsw/dhmsw/utils/snapimg.tiff'
im = imread(path)
#im = im[:,:,0]


###############################################################################
###  Define Parameters
###############################################################################
wl = [405e-9, 532e-9, 650e-9]
propagation_dist = [(1.6/100), (4.7/100), (6.6/100)]
chromatic_shift = [0, -3.6/100, -4.6/100] #None

###############################################################################
###  Create hologram object 
###############################################################################
# Create hologram
holo = Hologram(im, wavelength = wl)

###############################################################################
###  Create Spectral Masks 2048x2048x3
###############################################################################
N = holo.n

mask_list = np.zeros((N, N, len(wl)))
maskidx = 0
x, y = np.meshgrid(np.linspace(0,N,N),np.linspace(0,N,N))

centerx, centery = (1263, 1482)
#centerx, centery = (285, 200)
radius  = 250
mask = np.zeros(im.shape)
mask [ np.power(x-centerx,2) + np.power(y-centery, 2) < radius*radius ] = 1
mask_list[:,:,maskidx] = mask

maskidx += 1
#centerx, centery = (452, 1008)
centerx, centery = (1600, 1041)
radius  = 260
mask = np.zeros(im.shape)
mask [ np.power(x-centerx,2) + np.power(y-centery, 2) < radius*radius ] = 1
mask_list[:,:,maskidx] = mask

maskidx += 1
#centerx, centery = (667, 1608)
centerx, centery = (1382, 438)
radius  = 266 #250
mask = np.zeros(im.shape)
mask [ np.power(x-centerx,2) + np.power(y-centery, 2) < radius*radius ] = 1
mask_list[:,:,maskidx] = mask

###############################################################################
###  Compute Reconstruction
###############################################################################
import time
start_time = time.time()
#fourier_mask = Mask(holo.n, mask_list)
w = holo.my_reconstruct(propagation_dist, fourier_mask=None, chromatic_shift=chromatic_shift)
print("Elasped time to compute reconstruction: %f seconds"%(time.time()-start_time));
#sys.exit(0)


###############################################################################
###  Plot Intensity
###############################################################################
f, axes = plt.subplots(1, 1, sharex=True)
wv = 0
axes.imshow(np.log(np.abs(holo.ft_hologram)).astype(np.uint8))
plt.show()
f, axes = plt.subplots(1, 3, sharex=True)
wv = 0
axes[0].imshow(w.intensity[:,:,0,wv])
axes[1].imshow(w.intensity[:,:,1,wv])
axes[2].imshow(w.intensity[:,:,2,wv])
plt.show()
f, axes = plt.subplots(1, 3, sharex=True)
wv = 1
axes[0].imshow(w.intensity[:,:,0,wv])
axes[1].imshow(w.intensity[:,:,1,wv])
axes[2].imshow(w.intensity[:,:,2,wv])
plt.show()
f, axes = plt.subplots(1, 3, sharex=True)
wv = 2
axes[0].imshow(w.intensity[:,:,0,wv])
axes[1].imshow(w.intensity[:,:,1,wv])
axes[2].imshow(w.intensity[:,:,2,wv])
plt.show()

sys.exit(0)

###############################################################################
###  Plot Phase
###############################################################################
f, axes = plt.subplots(1, 3, sharex=True)
wv = 0
axes[0].imshow(w.phase[:,:,0,wv])
axes[1].imshow(w.phase[:,:,1,wv])
axes[2].imshow(w.phase[:,:,2,wv])
plt.show()
f, axes = plt.subplots(1, 3, sharex=True)
wv = 1
axes[0].imshow(w.phase[:,:,0,wv])
axes[1].imshow(w.phase[:,:,1,wv])
axes[2].imshow(w.phase[:,:,2,wv])
plt.show()
f, axes = plt.subplots(1, 3, sharex=True)
wv = 2
axes[0].imshow(w.phase[:,:,0,wv])
axes[1].imshow(w.phase[:,:,1,wv])
axes[2].imshow(w.phase[:,:,2,wv])
plt.show()


import sys
from shampoo.reconstruction import (Hologram)
from skimage.io import imread
import matplotlib.pyplot as plt
import numpy as np
import time
import sys

# Read file
#path = '/proj/dhm/sfregoso/data/USAF_test.tif'
path = './data/USAF_multi.tif'
im = imread(path)


# "Apodize" image - make the edges go to zero
N = im.shape[0]
x, y = np.meshgrid(np.linspace(0,N,N),np.linspace(0,N,N))


# Parameters
wl = [405e-9]
#wl = np.asarray((405e-9, 532e-9, 650e-9))
#d1 = -3.6/100
d1 = 0
#propagation_dist = [d1 + (1.6/100), d1 + (3.6/100), d1 + (6.6/100)]
propagation_dist = 3.6/100

# Create Spectral Mask
mask_list = np.zeros((N, N, len(wl)))
maskidx = 0

centerx, centery = (1263, 1482)
#centerx, centery = (285, 200)
radius  = 250
mask = np.zeros(im.shape)
mask [ np.power(x-centerx,2) + np.power(y-centery, 2) < radius*radius ] = 1
mask_list[:,:,maskidx] = mask


start_time = time.time()

# Create hologram
holo = Hologram(im, wavelength = wl)

print("Execution Time: %f seconds"%(time.time()-start_time))

start_time = time.time()

# Create hologram
ft_holo = holo.ft_hologram

print("Ft Holo Execution Time: %f seconds"%(time.time()-start_time))

sys.exit(0)

# Perform Reconstruction
#propagation_dist = 3.6/100

w = holo.reconstruct(propagation_dist, fourier_mask=None)

stop_time = time.time()
print("Execution Time: %f seconds"%(stop_time-start_time))

sys.exit(0)

f, axes = plt.subplots(1, 3, sharex=True)
wv = 0
axes[0].imshow(w.phase[:,:,0])
axes[1].imshow(w.phase[:,:,1])
axes[2].imshow(w.phase[:,:,2])
plt.show()

sys.exit(0)


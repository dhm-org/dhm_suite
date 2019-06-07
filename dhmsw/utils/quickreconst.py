import sys
from shampoo.reconstruction import (Hologram, arrshift)
from skimage.io import imread
import matplotlib.pyplot as plt
import numpy as np
import time
from shampoo.mask import (Circle, Mask)

path = './snapimg.tiff'
im = imread(path)
if im.ndim > 2:
    im = im[:,:,0]
################################################################################
###  Set Parameters
################################################################################
wl = np.asarray([405e-9, 532e-9, 650e-9])
propagation_dist = np.asarray(((1.6/100), (4.7/100), (6.6/100)))
plotimages = True

################################################################################
###  Define Fourier Masks
################################################################################
N = im.shape[0]
center_list = []
centerx, centery, radius = (1263, 1482, 250)
#centerx, centery, radius = (285, 200, 250)
center_list.append( Circle(centerx, centery, radius) )
centerx, centery, radius = (452, 1008, 260)
center_list.append( Circle(centerx, centery, radius) )
centerx, centery, radius = (667, 1608, 266)
center_list.append( Circle(centerx, centery, radius) )

fourier_mask = Mask(N, center_list[0:len(wl)])

holo = Hologram(im, wavelength=wl)

### Execute the G factor. 

holo.update_G_factor(propagation_dist)
G = holo.G

import time
start_time = time.time()
w = holo.my_reconstruct(propagation_dist, fourier_mask=fourier_mask, compute_digital_phase_mask=False, chromatic_shift=None)
print("Elapsed time: %f"%(time.time()-start_time))




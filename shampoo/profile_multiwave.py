###############################################################################
### CProfile:  python3 -m cProfile -s cumulative profile_multiwave.py > cprofile_20180731_TXT.txt
###
### LineProfiler:  /usr/local/python-3.6.4/bin/kernprof -l -v profile_multiwave.py
###############################################################################
import sys
from shampoo.reconstruction import (Hologram)
from skimage.io import imread
import matplotlib.pyplot as plt
import numpy as np
import time
#sys.path.insert(0, './shampoo/')
from shampoo.mask import (Circle, Mask)

PLOT = False

start_time = time.time()
# Read file
path = './data/USAF_multi.tif'
#path = '/proj/dhm/sfregoso/git_repos/dhmsw/dhmsw/utils/snapimg.tiff'
#path = '/proj/dhm/sfregoso/data/20180404_mako2048_ot_gr_bl_0.65/1759-off.bmp'
im = imread(path)
if im.ndim > 2:
    im = im[:,:,0]


###############################################################################
### Parameters
###############################################################################
wl = [435e-9, 535e-9, 635e-9]
#wl = [635e-9]
#d1 = -3.6/100
d1 = 0
#propagation_dist = [d1 + (1.6/100), d1 + (4.7/100), d1 + (6.6/100)]
propagation_dist = [0.01, 0.05, 0.1]
#propagation_dist = [0.01]
#propagation_dist = [(1.6/100)]
#chromatic_shift = [0, -3.6/100, -4.6/100]
#chromatic_shift = [0, 0, 0]
#chromatic_shift = [0, 0]
chromatic_shift = None
#chromatic_shift = [0]

###############################################################################
### Create Spectral Mask
###############################################################################
N = im.shape[0]
x, y = np.meshgrid(np.linspace(0,N,N),np.linspace(0,N,N))

mask_list = np.zeros((N, N, len(wl)))
maskidx = 0

center_list = []
#centerx, centery, radius = (1485, 1496, 200)
centerx, centery, radius = (1173, 605, 200)
#centerx, centery, radius = (1263, 1482, 250)
#centerx, centery, radius = (285, 200, 250)
center_list.append(Circle(centerx, centery, radius))
#centerx, centery, radius = (1455, 954, 200)
centerx, centery, radius = (1600, 1041, 260)
#centerx, centery, radius = (452, 1008, 260)
center_list.append(Circle(centerx, centery, radius))
#centerx, centery, radius = (1300, 1364, 200)
centerx, centery, radius = (1382, 438, 266)
#centerx, centery, radius = (667, 1608, 266)
center_list.append(Circle(centerx, centery, radius))

fourier_mask = Mask(N, center_list)
#for i in range(len(wl)):
#    centerx, centery, radius = center_list[i]
    #mask = np.zeros(im.shape)
    #mask [ np.power(x-centerx,2) + np.power(y-centery, 2) < radius*radius ] = 1
    #mask_list[:,:,i] = mask
    
#fourier_mask = np.asarray(mask_list, dtype=np.bool)

###############################################################################
# Create hologram
###############################################################################
holo = Hologram(im, wavelength = wl)
holo.ft_hologram # Calling this the first time creates the hologram

if PLOT:
    plt.imshow(np.log(np.abs(holo.ft_hologram)**2))
    plt.show()
    for i in range(len(wl)):
        plt.imshow(np.log(np.abs(holo.ft_hologram * fourier_mask.mask[:,:,i])**2))
    plt.show()
###############################################################################
# Update Chromatic shift
###############################################################################
holo.update_chromatic_shift(chromatic_shift)

###############################################################################
# Update G Factor
###############################################################################
holo.update_G_factor(propagation_dist)
print("Setup Elapsed Time: %.2f seconds"%(time.time() - start_time))
for i in range(5):
    
    ###############################################################################
    # Compute Reconstruction
    ###############################################################################
    start_time=time.time()
    #w = holo.my_reconstruct(propagation_dist, fourier_mask=fourier_mask, compute_digital_phase_mask=False, chromatic_shift=None)
    w = holo.my_reconstruct(propagation_dist, compute_digital_phase_mask=False, chromatic_shift=None)
    #w = holo.my_reconstruct(propagation_dist, fourier_mask=None, chromatic_shift=None)
    print("my_reconstruct() Elapsed Time: %.2f seconds"%(time.time() - start_time))
    
    w.phase
    print('w.phase.shape = ', w.phase.shape)
    if PLOT:
        for i in range(len(wl)):
            for j in range(len(propagation_dist)):
                plt.figure()
                #plt.imshow(np.abs(w.amplitude[:,:,j,i]))
                plt.imshow(np.abs(w.phase[:,:,j,i]))
        plt.show()


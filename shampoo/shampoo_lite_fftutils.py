import sys
from shampoo.reconstruction import (Hologram, arrshift)
from skimage.io import imread
import matplotlib.pyplot as plt
import numpy as np
import time
import h5py
sys.path.insert(0,'./shampoo/')
from mask import (Circle, Mask)

from fftutils import (FFT, fftshift)

################################################################################
###  Read File
################################################################################
path = '/proj/dhm/sfregoso/data/USAF_multi.tif'
path = '/proj/dhm/sfregoso/data/20180404_mako2048_ot_gr_bl_0.65/1759-off.bmp'
im = imread(path)


if True:
    fft = FFT(im.shape, np.float32, np.complex64, threads=24)
    fft2 = fft.fft2
    ifft2 = fft.ifft2
else:
    #from pyfftw.interfaces.scipy_fftpack import fft2, ifft2
    from scipy.fftpack import fft2, ifft2

################################################################################
###  Set Parameters
################################################################################
wl = np.asarray([405e-9, 532e-9, 650e-9])
wl = np.asarray([405e-9])
propagation_dist = np.asarray(((1.6/100), (4.7/100), (6.6/100)))
#propagation_dist = np.asarray([(1.6/100)])
plotimages = True

################################################################################
###  Define Fourier Masks
################################################################################
N = im.shape[0]
center_list = []
#centerx, centery, radius = (1263, 1482, 250)
centerx, centery, radius = (1483, 1497, 250)
#centerx, centery, radius = (285, 200, 250)
center_list.append( Circle(centerx, centery, radius) )
centerx, centery, radius = (1600, 1041, 260)
#centerx, centery, radius = (452, 1008, 260)
center_list.append( Circle(centerx, centery, radius) )
centerx, centery, radius = (1382, 438, 266)
#centerx, centery, radius = (667, 1608, 266)
center_list.append( Circle(centerx, centery, radius) )

fourier_mask = Mask(N, center_list[0:len(wl)])

#N = im.shape[0]
#x, y = np.meshgrid(np.linspace(0,N,N),np.linspace(0,N,N))
#
#mask_list = np.zeros((N, N, len(wl)))
#maskidx = 0
#
#center_list = []
#centerx, centery, radius = (1263, 1482, 250)
##centerx, centery, radius = (285, 200, 250)
#center_list.append((centerx, centery, radius))
#centerx, centery, radius = (1600, 1041, 260)
##centerx, centery, radius = (452, 1008, 260)
#center_list.append((centerx, centery, radius))
#centerx, centery, radius = (1382, 438, 266)
##centerx, centery, radius = (667, 1608, 266)
#center_list.append((centerx, centery, radius))
#
#for i in range(len(wl)):
#    centerx, centery, radius = center_list[i]
#    mask = np.zeros(im.shape)
#    mask [ np.power(x-centerx,2) + np.power(y-centery, 2) < radius*radius ] = 1
#    mask_list[:,:,i] = mask
#    
#fourier_mask = np.asarray(mask_list, dtype=np.bool)

###############################################################################
####  Compute propagator (G)
###############################################################################
# NOTE:  This can be placed in a database
N = im.shape[0]
dx = 3.45e-6
dy = 3.45e-6
#x, y =  holo.mgrid - N/2 #np.mgrid[0:self.n, 0:self.n] - holo.n/2
x, y =  np.mgrid[0:N, 0:N] - N/2

computeGtime = time.time()
myG = np.zeros((N, N, len(propagation_dist), len(wl)), dtype=np.complex64)
for li in range(len(wl)):
    wvl = wl[li]
    for di in range(len(propagation_dist)):
        d = propagation_dist[di]
        first_term =  (wvl**2.0 * (x + N**2. * dx**2./(2.0 * d * wvl))**2 / (N**2. * dx**2.))
        second_term = (wvl**2.0 * (y + N**2. * dy**2./(2.0 * d * wvl))**2 / (N**2. * dy**2.))
        myG[:,:,di,li] = np.exp(-1j * 2.* np.pi * (d / wvl) * np.sqrt(1. - first_term - second_term))
print("G Computation Time: %f sec\n"%(time.time()-computeGtime))

################################################################################
###  Create Hologram Object
################################################################################
### Prepare Hologram
# Crops the image to the lowest dimension and makes it square dimensions if its non-square
# Rebins the hologram.  NOTE if rebin == 1 then no rebinning is done
#holo = Hologram(im, wavelength = wl)


#fft = FFT(im.shape, np.float64, np.complex128, threads=24)

for _ in range(1):
    ###############################################################################
    ###  Start the timer to meausre performance
    ###############################################################################
    start_time = time.time()
    ################################################################################
    ###  Compute FFT of raw hologram
    ################################################################################
    fft_holo = fft2(im)
    
    # Reorders FFT
    ft_hologram = fftshift(fft_holo.astype(np.complex64))
    #ft_hologram = holo.ft_hologram # NOTE  apodizes, fft and reorders
    
    print("FFT of raw hologram Elapsed Time: %.2f"%(time.time()-start_time))
    
    #view fft in log  NOTE this 
    if plotimages:
        plt.figure()
        plt.imshow(np.log(np.abs(fft_holo)**2))
        
        # Plot reordere FFT
        plt.figure()
        plt.imshow(np.log(np.abs(ft_hologram)**2))
        
        plt.show()
    
    
    ################################################################################
    ###  Compute R (reference wave?)  digital Phase Mask
    ################################################################################
    R = np.ones((N,N, len(wl)), dtype=ft_hologram.dtype)
    
    ################################################################################
    ### Applie mask and move fourier masked spectra to center of image 
    ################################################################################
    Fh = np.zeros((N,N, len(wl)), dtype=ft_hologram.dtype)
    
    for l in range(len(wl)):
        Fh[:,:,l] = ft_hologram * fourier_mask.mask[:,:,l] * R[:,:,l]
    
    # Plot each Masked fourier space
    if plotimages:
        for i in range(Fh.shape[2]):
            plt.figure()
            plt.imshow(np.log(np.abs(Fh[:,:,i])**2))
        plt.show()
    
    for l in range(len(wl)):
        centerx = fourier_mask.circle_list[l].centerx
        centery = fourier_mask.circle_list[l].centery
    
        # NOTE: The axes centers used are reversed
        Fh[:,:,l] = arrshift(Fh[:,:,l], [-centery, -centerx], axes=(0,1))
    
    if plotimages:
        for i in range(Fh.shape[2]):
            plt.figure()
            plt.imshow(np.log(np.abs(Fh[:,:,i])**2))
        plt.show()
    
    completeReconstTime = time.time()
    Psi = np.zeros((N, N, len(propagation_dist), len(wl)), dtype=ft_hologram.dtype)
    for li in range(len(wl)):
        for di in range(len(propagation_dist)):
            Psi[:,:,di,li] = fftshift(ifft2(Fh[:,:,li] * myG[:,:,di,li]))
    print("Reconst Elapsed Time: %.2f"%(time.time() - completeReconstTime))
    
    print("Elapsed Time: %.2f"%(time.time()-start_time))

sys.exit(0)
for i in range(len(wl)):
    for j in range(len(propagation_dist)):
        plt.figure()
        plt.imshow(np.abs(Psi[:,:,j,i]))

plt.show()


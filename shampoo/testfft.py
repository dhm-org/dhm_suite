from shampoo.fftutils import FFT, FFT_3 
from shampoo.reconstruction import (Hologram, fftshift)
import scipy
import numpy as np
from skimage.io import imread
import time
import timeit

myFFT3 = FFT_3((2048,2048,1), np.float32, np.complex64, threads=12)

path = './data/USAF_multi.tif'
im = imread(path)

### pyFFT via fftutils
start_time = time.time()
myFFT3.fft2(im)
print('fftutils fft2 elapsed time: %f'%(time.time()-start_time))
start_time = time.time()
ft_holo = myFFT3.fft2(im).astype(np.complex64)
print('fftutils fft2 with type conversion elapsed time: %f'%(time.time()-start_time))
print(ft_holo.dtype)

###
start_time = time.time()
ft_holo = scipy.fftpack.fft2(im)
print('scipy fft2 elapsed time: %f'%(time.time()-start_time))

start_time = time.time()
ft_holo = np.fft.fft2(im)
print('numpy fft2 elapsed time: %f'%(time.time()-start_time))


holo = Hologram(im, wavelength = [405e-9])
start_time = time.time()
ft_holo = myFFT3.fft2(im)
ft_holo = fftshift(ft_holo)
print('FT hologram through shampoo elapsed time: %f'%(time.time()-start_time))

start_time = time.time()
ft_holo = myFFT3.fft2(im)
ft_holo = np.fft.fftshift(ft_holo)
print('FT hologram shifted with numpy elapsed time: %f'%(time.time()-start_time))

start_time = time.time()
ft_holo = myFFT3.fft2(im)
ft_holo = scipy.fftpack.fftshift(ft_holo)
print('FT hologram shifted with scipy elapsed time: %f'%(time.time()-start_time))



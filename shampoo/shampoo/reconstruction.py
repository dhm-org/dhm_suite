"""
This module handles reconstruction of phase and intensity images from raw
holograms using "the convolution approach": see Section 3.3 of Schnars & Juptner
(2002) Meas. Sci. Technol. 13 R85-R101 [1]_.

Aberration corrections from Colomb et al., Appl Opt. 2006 Feb 10;45(5):851-63
are applied [2]_.

    .. [1] http://x-ray.ucsd.edu/mediawiki/images/d/df/Digital_recording_numerical_reconstruction.pdf
    .. [2] http://www.ncbi.nlm.nih.gov/pubmed/16512526

"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from collections import Sized, deque, defaultdict

import warnings

from multiprocessing import Pool 
import multiprocessing
from functools import partial

from .vis import save_scaled_image

import numpy as np
from numpy.compat import integer_types

from scipy.ndimage import gaussian_filter, maximum_filter
from scipy.signal import tukey

from skimage.restoration import unwrap_phase as skimage_unwrap_phase
from skimage.io import imread
from skimage.feature import blob_doh

#from astropy.utils.exceptions import AstropyUserWarning

import matplotlib.pyplot as plt

import time

from shampoo.mask import (Circle, Mask)
from shampoo.g_factor import compute_G_factor

from .fftutils import FFT_3 

FLOATDTYPE = np.float32
COMPLEXDTYPE = np.complex64
FRAMEDIMENSIONS = (2048, 2048, 1)
NUMFFTTHREADS = multiprocessing.cpu_count()/2
myFFT3 = None
fft3   = None
ifft3  = None
fft2   = None
ifft2  = None

myFFT3 = FFT_3(FRAMEDIMENSIONS, FLOATDTYPE, COMPLEXDTYPE, threads=NUMFFTTHREADS)
fft3   = myFFT3.fft3
ifft3  = myFFT3.ifft3
fft2   = myFFT3.fft2
ifft2  = myFFT3.ifft2
print("Importing fft2 and ifft2 from fftutils")

__all__ = ['Hologram', 'ReconstructedWave', 'unwrap_phase']
RANDOM_SEED = 42
TWO_TO_N = [2**i for i in range(13)]


def rebin_image(a, binning_factor):
    # Courtesy of J.F. Sebastian: http://stackoverflow.com/a/8090605
    if binning_factor == 1:
        return a

    new_shape = (a.shape[0]/binning_factor, a.shape[1]/binning_factor)
    sh = (new_shape[0], a.shape[0]//new_shape[0], new_shape[1],
          a.shape[1]//new_shape[1])
    return a.reshape(map(int, sh)).mean(-1).mean(1)

def fftshift(x, additional_shift=None, axes=None):
    """
    Shift the zero-frequency component to the center of the spectrum, or with
    some additional offset from the center.

    This is a more generic fork of `~numpy.fft.fftshift`, which doesn't support
    additional shifts.


    Parameters
    ----------
    x : array_like
        Input array.
    additional_shift : list of length ``M``
        Desired additional shifts in ``x`` and ``y`` directions respectively
    axes : int or shape tuple, optional
        Axes over which to shift.  Default is None, which shifts all axes.

    Returns
    -------
    y : `~numpy.ndarray`
        The shifted array.
    """
    tmp = np.asarray(x)
    ndim = len(tmp.shape)
    if axes is None:
        axes = list(range(ndim))
    elif isinstance(axes, integer_types):
        axes = (axes,)

    # If no additional shift is supplied, reproduce `numpy.fft.fftshift` result
    if additional_shift is None:
        additional_shift = [0, 0]

    y = tmp
    for k, extra_shift in zip(axes, additional_shift):
        n = tmp.shape[k]
        if (n+1)//2 - extra_shift < n:
            p2 = (n+1)//2 - extra_shift
        else:
            p2 = abs(extra_shift) - (n+1)//2
        mylist = np.concatenate((np.arange(p2, n), np.arange(0, p2)))
        y = np.take(y, mylist, k)
    return y
    
def arrshift(x, shift, axes=None):
    """
    Shift array by ``shift`` along ``axes``.


    Parameters
    ----------
    x : array_like
        Input array.
    shift : list of length ``M``
        Desired additional shifts along respective axes
    axes : int or shape tuple, optional
        Axes over which to shift.  Default is None, which shifts all axes.

    Returns
    -------
    y : `~numpy.ndarray`
        The shifted array.
    """
    y = np.asarray(x)
    ndim = len(y.shape)
    if axes is None:
        axes = list(range(ndim))
    elif isinstance(axes, integer_types):
        axes = (axes,)
    
    for j, k in zip(axes, shift):
        n = y.shape[j];
        y = np.roll(y, (n+1)//2 - (-1)*k, axis=j)
    
    return y

def _load_hologram(hologram_path):
    """
    Load a hologram from path ``hologram_path`` using scikit-image and numpy.
    """
    im = np.array(imread(hologram_path), dtype=FLOATDTYPE)
    # Some TIF images are saved as 3D arrays (one slice per color)
    if im.ndim == 3:
        warnings.warn('Image at {} is not grayscale. Only considering the first slice.'.format(hologram_path), UserWarning)
        return im[:,:,0]
    return im


def _find_peak_centroid(image, wavelength=405e-9, gaussian_width=10):
    """
    Smooth the image, find centroid of peak in the image.
    """
    wavelength = np.atleast_1d(wavelength).reshape((1,1,-1))
    F = gaussian_filter(image, gaussian_width) # Filter with a gaussian
    M = maximum_filter(F,3) # Get 8-neighbor maxima
    tfm = M==F # Maxima location TF array
    m = F[tfm] # Maxima
    idx = m.argsort()[::-1] # Sort the maxima, get the sorted indices in descending order
    x, y = np.nonzero(tfm) # Maxima locations
    # Grab top 2*#wavelengths + 1 peaks
    x = x[idx[0:(2*wavelength.shape[2]+1)]]
    y = y[idx[0:(2*wavelength.shape[2]+1)]]
    rsq = (x-image.shape[0]/2)**2 + (y-image.shape[1]/2)**2
    dist = np.sort(rsq)[1:] # Sort distances in ascending order
    idx = np.argsort(rsq)[1:] # Get sorted indices
    order = wavelength.reshape(-1).argsort()
    peaks = np.zeros([wavelength.shape[2],2])
    for o in order:
        i1 = idx[2*o]
        i2 = idx[2*o + 1]
        y1 = y[i1]
        y2 = y[i2]
        i = i1
        if y1 < y2:
            i = i2
        peaks[o,:] = [x[i], y[i]]
        
    return peaks

def _crop_image(image, crop_fraction):
    """
    Crop an image by a factor of ``crop_fraction``.
    """
    if crop_fraction == 0:
        return image

    crop_length = int(image.shape[0] * crop_fraction)

    if crop_length not in TWO_TO_N:
        message = ("Final dimensions after crop should be a power of 2^N. "
                   "Crop fraction of {0} yields dimensions ({1}, {1})"
                   .format(crop_fraction, crop_length))
        warnings.warn(message, CropEfficiencyWarning)

    cropped_image = image[crop_length//2:crop_length//2 + crop_length,
                          crop_length//2:crop_length//2 + crop_length]
    return cropped_image

def _crop_to_square(image, two_pwr_N_square_up=True):
    """
    Ensure that hologram is square.

    square_up:  True it will reshape to largest dimension, else to smallest dimension
    """
    import math

    sh = image.shape
   
    if sh[0] == sh[1]:
        square_image = image
    else:
        if two_pwr_N_square_up:
            N = 2 ** int(math.log(max(sh), 2))
            square_image = np.zeros((N, N), dtype=image.dtype)
            temp_sh = (sh[0] if N > sh[0] else N, sh[1] if N > sh[1] else N)
            #print(temp_sh)
            square_image[:temp_sh[0],:temp_sh[1]] = image[:temp_sh[0], :temp_sh[1]]
        else:
            square_image = image[:min(sh), :min(sh)]

    return square_image


class CropEfficiencyWarning(Warning):
    pass
    
class MaskSizeWarning(Warning):
    pass
    
class UpdateError(Exception):
    pass
        
class SizeError(Exception):
    pass

class Hologram(object):
    """
    Container for holograms and methods to reconstruct them.
    """
    def __init__(self, hologram, crop_fraction=None, wavelength=405e-9,
                 rebin_factor=1, dx=3.45e-6, dy=3.45e-6, mask=None):
        """
        Parameters
        ----------
        hologram : `~numpy.ndarray`
            Input hologram. If the hologram was taken with multiple wavelengths,
            the array should be a stack of single-wavelength hologram along axis 2.
        crop_fraction : float
            Fraction of the image to crop for analysis
        wavelength : float [meters] or iterable
            Wavelength of laser. Multiple wavelengths can be given as well.
        rebin_factor : int
            Rebin the image by factor ``rebin_factor``. Must be an even integer.
        dx : float [meters]
            Pixel width in x-direction (unbinned)
        dy : float [meters]
            Pixel width in y-direction (unbinned)

        Notes
        -----
        Non-square holograms will be cropped to a square with the dimensions of
        the smallest dimension. TODO: Why are we not zero-filling out to the next
        power of 2 instead of cropping?
        """
        wavelength = np.atleast_1d(wavelength).reshape((1,1,-1)).astype(FLOATDTYPE)

        self.crop_fraction = crop_fraction
        self.rebin_factor = rebin_factor

        hologram = np.asarray(hologram, dtype = FLOATDTYPE)
        if hologram.ndim != 2:
            raise ValueError('hologram dimensions ({}) are invalid. Holograms should be 2D image'.format(hologram.shape))
        # Rebin the hologram
        square_hologram = _crop_to_square(hologram)
        binned_hologram = rebin_image(square_hologram, self.rebin_factor)

        # Crop the hologram by factor crop_factor, centered on original center
        if crop_fraction is not None:
            self.hologram = _crop_image(binned_hologram, crop_fraction)
        else:
            self.hologram = binned_hologram
        
        self.n = self.hologram.shape[0]
        self.wavelength = wavelength
        self.wavenumber = 2*np.pi/self.wavelength
        self._spectral_peak = None
        self._chromatic_shift = None
        self.dx = dx*rebin_factor
        self.dy = dy*rebin_factor
        self.random_seed = RANDOM_SEED
        self.apodization_window_function = None
        self._ft_hologram = None;
        #self.mgrid = np.mgrid[0:self.n, 0:self.n] ## Takes a lot of time to create
        self._mgrid = None
        self.G = None
        self.mask = mask
        self.x_peak = None
        self.y_peak = None

        global FRAMEDIMENSIONS
        global myFFT3
        global fft3
        global ifft3
        global fft2
        global ifft2
        if self.wavelength.size != FRAMEDIMENSIONS[2] or self.n != FRAMEDIMENSIONS[1]:
            global myFFT3, fft3, ifft3, fft2, ifft2
            #print("$$$$$$$$ Adjusted FFT $$$$$$$$$$$")
            FRAMEDIMENSIONS = (self.n, self.n, self.wavelength.size)
            #print("Updating FFT shape", FRAMEDIMENSIONS)
            myFFT3 = FFT_3(FRAMEDIMENSIONS, FLOATDTYPE, COMPLEXDTYPE, threads=NUMFFTTHREADS)
            fft3 = myFFT3.fft3
            ifft3 = myFFT3.ifft3
            fft2 = myFFT3.fft2
            ifft2 = myFFT3.ifft2

    def update_hologram(self, hologram, crop_fraction=None, wavelength=None,
                 rebin_factor=None, dx=None, dy=None, mask=None):
        """
        Parameters
        ----------
        hologram : `~numpy.ndarray`
            Input hologram. If the hologram was taken with multiple wavelengths,
            the array should be a stack of single-wavelength hologram along axis 2.
        crop_fraction : float
            Fraction of the image to crop for analysis
        wavelength : float [meters] or iterable
            Wavelength of laser. Multiple wavelengths can be given as well.
        rebin_factor : int
            Rebin the image by factor ``rebin_factor``. Must be an even integer.
        dx : float [meters]
            Pixel width in x-direction (unbinned)
        dy : float [meters]
            Pixel width in y-direction (unbinned)

        Notes
        -----
        Non-square holograms will be cropped to a square with the dimensions of
        the smallest dimension. TODO: Why are we not zero-filling out to the next
        power of 2 instead of cropping?
        """

      
        if crop_fraction is not None:  self.crop_fraction = crop_fraction
        if rebin_factor is not None: self.rebin_factor = rebin_factor

        hologram = np.asarray(hologram, dtype = FLOATDTYPE)
        if hologram.ndim != 2:
            raise ValueError('hologram dimensions ({}) are invalid. Holograms should be 2D image'.format(hologram.shape))
        # Rebin the hologram
        square_hologram = _crop_to_square(hologram)
        binned_hologram = rebin_image(square_hologram, self.rebin_factor)

        # Crop the hologram by factor crop_factor, centered on original center
        if self.crop_fraction is not None:
            self.hologram = _crop_image(binned_hologram, self.crop_fraction)
        else:
            self.hologram = binned_hologram
        
        self.n = self.hologram.shape[0]

        if wavelength is not None:
            wavelength = np.atleast_1d(wavelength).reshape((1,1,-1)).astype(FLOATDTYPE)
            self.wavelength = wavelength
            self.wavenumber = 2*np.pi/self.wavelength

        #self._spectral_peak = None
        #self._chromatic_shift = None
        if dx is not None:  self.dx = dx*self.rebin_factor
        if dy is not None:  self.dy = dy*self.rebin_factor
        #self.random_seed = RANDOM_SEED
        #self.apodization_window_function = None
        self._ft_hologram = None;
        #self.mgrid = np.mgrid[0:self.n, 0:self.n] ## Takes a lot of time to create
        #self._mgrid = None
        #self.G = None

        global FRAMEDIMENSIONS
        global myFFT3
        global fft3
        global ifft3
        global fft2
        global ifft2
        if self.wavelength.size != FRAMEDIMENSIONS[2] or self.n != FRAMEDIMENSIONS[1]:
            global myFFT3, fft3, ifft3, fft2, ifft2
            #print("$$$$$$$$ Adjusted FFT $$$$$$$$$$$")
            #print("wavelength.size, self.n, FRAMEDDIMENSIONS[2]: ", self.wavelength.size, self.n, FRAMEDIMENSIONS[2])
            FRAMEDIMENSIONS = (self.n, self.n, self.wavelength.size)
            #print("Updating FFT shape", FRAMEDIMENSIONS)
            myFFT3 = FFT_3(FRAMEDIMENSIONS, FLOATDTYPE, COMPLEXDTYPE, threads=NUMFFTTHREADS)
            fft3 = myFFT3.fft3
            ifft3 = myFFT3.ifft3
            fft2 = myFFT3.fft2
            ifft2 = myFFT3.ifft2
            self._mgrid = None
            self.mgrid

    def set_wavelength(self, wavelength):
        wavelength = np.atleast_1d(wavelength).reshape((1,1,-1)).astype(FLOATDTYPE)
        self.wavelength = wavelength
        self.wavenumber = 2*np.pi/self.wavelength

    def set_dx(self, dx):
        self.dx = dx * self.rebin_factor

    def set_dy(self, dy):
        self.dy = dy * self.rebin_factor

    def set_hologram(self, hologram):
        hologram = np.asarray(hologram, dtype = FLOATDTYPE)
        if hologram.ndim != 2:
            raise ValueError('hologram dimensions ({}) are invalid. Holograms should be 2D image'.format(hologram.shape))
        # Rebin the hologram
        square_hologram = _crop_to_square(hologram)
        binned_hologram = rebin_image(square_hologram, self.rebin_factor)

        # Crop the hologram by factor crop_factor, centered on original center
        if self.crop_fraction is not None:
            self.hologram = _crop_image(binned_hologram, crop_fraction)
        else:
            self.hologram = binned_hologram
        
        self.n = self.hologram.shape[0]

    @property
    def mgrid(self):
        if self._mgrid is None:
            self._mgrid = np.mgrid[0:self.n, 0:self.n]
        return self._mgrid

    @property
    #def ft_hologram(self, apodize=True):
    def ft_hologram(self, apodize=False):
        """
        `~numpy.ndarray` of the self.hologram FFT
        """
        if self._ft_hologram is None:
            if apodize==True:
                apodized_hologram = self.apodize(self.hologram)
                self._ft_hologram = fftshift(fft2(apodized_hologram))
            else:
                self._ft_hologram = fftshift(fft2(self.hologram))

        return self._ft_hologram

    def update_ft_hologram(self, apodize=False):
        if apodize==True:
            apodized_hologram = self.apodize(self.hologram)
            self._ft_hologram = fftshift(fft2(apodized_hologram))
        else:
            self._ft_hologram = fftshift(fft2(self.hologram))

        return self._ft_hologram
        
    @property
    def spectral_peak(self):
        if self._spectral_peak is None:
            # Guess 'em
            self.update_spectral_peak(self.fourier_peak_centroid())
        
        return self._spectral_peak
        
    @property
    def chromatic_shift(self):
        if self._chromatic_shift is None:
            self._chromatic_shift = np.zeros_like(self.wavelength);
            # Ideally we'd actually calculate the chromatic shift
        return self._chromatic_shift

    @classmethod
    def from_tif(cls, hologram_path, **kwargs):
        """
        Load a hologram from a TIF file.

        This class method takes the path to the TIF file as the first argument.
        All other arguments are the same as `~shampoo.Hologram`.

        Parameters
        ----------
        hologram_path : str
            Path to the hologram to load
        """
        hologram = _load_hologram(hologram_path)
        return cls(hologram, **kwargs)

    #@profile
    def get_masked_spectra(self, ft_hologram, mask, x_peak, y_peak):
        """
        Apply mask to fourier hologram
         
        Parameters
        ---------
        ft_hologram : np.array 
            2D FFT of hologram
        mask: np.array dtype=np.bool    
            3D boolean mask were dimenstions are (N, N, wavelength.size)
        x_peak: np.array
            int array (wavelength.size, 1) containing X center of mask
        y_peak: np.array
            int array (wavelength.size, 1) containing Y center of mask
        """

        Fh = np.zeros((self.n, self.n, self.wavelength.size), dtype=ft_hologram.dtype)
        #Fh = np.zeros((self.n, self.n, len(self.wavelength)), dtype=ft_hologram.dtype)
        for l in range(self.wavelength.size):
        #for l in range(len(self.wavelength)):
            if(l < x_peak.size):
                centerx = x_peak[l]
            if(l < y_peak.size):
                centery = y_peak[l]
            # NOTE: The axes centers used are reversed
            #print("get_masked_spectral: ", ft_hologram.shape, mask[:,:,l].shape)
            if(l < mask.shape[2]):
                m = mask[:,:,l];
            else:
                m = mask[:,:,0];
            Fh[:,:,l] = arrshift(ft_hologram * m, [-centerx, -centery], axes=(0,1))
        return Fh

    #@profile
    def compute_spectral_peak_mask(self, mask_radius=150):

        self._spectral_peak = None
        x_peak, y_peak = self.spectral_peak

        # Calculate mask radius. TODO: Update 250 to an automated guess based on input values.
        if self.rebin_factor != 1:
            #mask_radius = 150./self.rebin_factor
            mask_radius /= self.rebin_factor
        elif self.crop_fraction is not None and self.crop_fraction != 0:
            #mask_radius = 150.*self.crop_fraction
            mask_radius *= self.crop_fraction

        self.mask = self.real_image_mask(x_peak, y_peak, mask_radius)
        return x_peak, y_peak, self.mask

    def my_reconstruct(self, propagation_distance, compute_spectral_peak=False, compute_digital_phase_mask=False, digital_phase_mask=None, fourier_mask=None, chromatic_shift=None, G_factor=None):
        
        #start_time = time.time()
        propagation_distance = np.atleast_1d(propagation_distance).reshape((1,1,-1)).astype(FLOATDTYPE)

        if chromatic_shift is not None:
            self.update_chromatic_shift(chromatic_shift)

        ################################################################################
        ###  Compute G propagator if not yet created
        ################################################################################
        if G_factor is not None:
            self.set_G_factor(G_factor)

        if self.G is None:
            self.update_G_factor (propagation_distance)

        ft_hologram = self.ft_hologram 

        ################################################################################
        ### Create mask from spectral peak OR Use user defined mask
        ################################################################################
        x_peak = self.x_peak
        y_peak = self.y_peak

        if self.mask is not None:
            if x_peak is None or y_peak is None:
                x_peak, y_peak = self.spectral_peak
                self.x_peak = x_peak
                self.y_peak = y_peak
            pass
        elif fourier_mask is None or compute_spectral_peak:
            x_peak, y_peak, self.mask = self.compute_spectral_peak_mask(mask_radius=150)
        else:
            #mask = np.asarray(fourier_mask, dtype=np.bool)
            self.mask = fourier_mask.mask
            x_peak = np.zeros((len(fourier_mask.circle_list), 1), dtype=np.int)
            y_peak = np.zeros((len(fourier_mask.circle_list), 1), dtype=np.int)
            for _ in range(len(fourier_mask.circle_list)):
                x_peak[_] = fourier_mask.circle_list[_].centery 
                y_peak[_] = fourier_mask.circle_list[_].centerx 

        if self.mask is not None:
            self.mask = np.atleast_3d(self.mask)

        print("propagation_distance.size=%d, self.wavelength.size=%d, self.mask=%d"%(propagation_distance.size, self.wavelength.size, self.mask.size))
        wave = np.zeros((self.n, self.n, propagation_distance.size, self.wavelength.size), dtype=ft_hologram.dtype)

        ### Apply mask to FFT of hologram and move to center 

        Fh = self.get_masked_spectra(ft_hologram, self.mask, x_peak, y_peak)

        print("Size of Fh: ", Fh.shape)
        if compute_digital_phase_mask:
            ################################################################################
            ###  Compute R (reference wave?)  digital Phase Mask
            ################################################################################
            psi = np.zeros((self.n, self.n, propagation_distance.size, self.wavelength.size), dtype=ft_hologram.dtype)

            start_time = time.time()
            for di in range(propagation_distance.size):
                #psi_[:,:,di,:] = self.apodized(Fh * self.G[:,:,di,:])
                dig_phase_mask = self.get_digital_phase_mask(np.atleast_3d(self.apodize(Fh * self.G[:,:,di,:]))) 
                for channel in range(self.wavelength.size):
                    psi[:,:,di,channel] = arrshift(fftshift(fft2(self.apodize(self.hologram) * dig_phase_mask[:,:,channel]
                                            ).astype(COMPLEXDTYPE)) *
                                            self.mask[:,:,channel],
                                            [-x_peak[channel],
                                             -y_peak[channel]],
                                            axes = (0,1))# * self.G[:,:,di,channel]
                    print("ET=%f sec"%(time.time()-start_time))

            for li in range(self.wavelength.size):
                for di in range(propagation_distance.size):
                    wave[:,:,di,li] = fftshift(ifft2(psi[:,:,di,channel] * self.G[:,:,di,li]))


        else:
            ################################################################################
            ### Applie mask and move fourier masked spectra to center of image 
            ################################################################################
            for di in range(propagation_distance.size):
                a = ifft3(Fh * self.G[:,:,di,:])
                wave[:,:,di,:] = fftshift(a)
#            for li in range(self.wavelength.size):
#                for di in range(propagation_distance.size):
#                    #a = Fh[:,:,li] * self.G[:,:,di,li]
#                    #b = ifft2(a)
#                    #c = fftshift(b)
#                    #wave[:,:,di,li] = c
#                    wave[:,:,di,li] = fftshift(ifft2(Fh[:,:,li] * self.G[:,:,di,li]))

        #print("my_reconstruction Execution Time: %f sec"%(time.time()-start_time))
        return ReconstructedWave(reconstructed_wave = wave, fourier_mask = self.mask, 
                                 wavelength = self.wavelength, depths = propagation_distance)

    def reconstruct(self, propagation_distance, spectral_peak=None, fourier_mask=None, chromatic_shift=None):
        """
        Reconstruct the hologram at all ``propagation_distance`` for all ``self.wavelength``.
        
        Parameters
        ----------
        propagation_distances : float or iterable of float
            Propagation distance(s) to reconstruct
        spectral_peak : `~numpy.ndarray`
            Centroid of spectral peak for wavelength in power spectrum of hologram FT
            (len(self.wavelength) x 2)
        fourier_mask : array_like or None, optional
            Fourier-domain mask. If None (default), a mask is determined from the position of the
            main spectral peak. If array_like, the array will be cast to boolean.

        Returns
        -------
        reconstructed : ReconstructedWave
            Container object for the reconstructed wave.
        """

        propagation_distance = np.atleast_1d(propagation_distance).astype(FLOATDTYPE)

        # Determine location of spectral peak
        # Did we specify a centroid? OK, use it.
        if spectral_peak is not None:
            self.update_spectral_peak(spectral_peak) 
            
        if chromatic_shift is not None:
            self.update_chromatic_shift(chromatic_shift)

        #SFF
        self.update_G_factor (propagation_distance)
        self.G = np.empty ((self.n, self.n, propagation_distance.size, self.wavelength.size), dtype=COMPLEXDTYPE)
        for channel in range(propagation_distance.size):
            self.G[:,:,channel,:] = self.fourier_trans_of_impulse_resp_func(np.atleast_1d([propagation_distance[channel]]*
                                    self.wavelength.size).reshape((1,1,-1))-self.chromatic_shift)
            
        # Ignore Fourier masks that are of incorrect shape
        if fourier_mask is not None and (np.prod(fourier_mask.shape) != 
           #np.prod(self.hologram.shape)*np.prod(self.wavelength.shape)*np.prod(propagation_distance.shape)):
           np.prod(self.hologram.shape)*np.prod(self.wavelength.shape)):
            fourier_mask = None
            message = ("Fourier mask dimensions don't match hologram dimensions. Ignoring.")
            warnings.warn(message, MaskSizeWarning)
        
        if propagation_distance.size > 1:
            wave =  self._reconstruct_multithread(propagation_distance, fourier_mask = fourier_mask)
        else:
            wave = self._reconstruct(propagation_distance, fourier_mask)
            wave = np.expand_dims(wave, axis = 2)   # single prop. distance will have the wrong shape
        
        # TODO: unwrap phase here
        return ReconstructedWave(reconstructed_wave = wave, fourier_mask = fourier_mask, 
                                 wavelength = self.wavelength, depths = propagation_distance)

    def _reconstruct(self, propagation_distance, compute_digital_phase_mask=True, fourier_mask=None):
        """
        Reconstruct the wave at a single ``propagation_distance`` for a single ``wavelength``.

        Parameters
        ----------
        propagation_distance : float
            Propagation distance [m]
        spectral_peak : integer pair [x,y]
            Centroid of spectral peak for wavelength in power spectrum of hologram FT
        fourier_mask : array_like or None, optional
            Fourier-domain mask. If None (default), a mask is determined from the position of the
            main spectral peak.

        Returns
        -------
        reconstructed_wave : `~numpy.ndarray` ndim 3
            The reconstructed wave as an array of dimensions (X, Y, wavelengths)
        """
        
        # Either use a Fourier-domain mask based on coords of spectral peak,
        # or a user-specified mask
        x_peak = np.zeros((self.wavelength.size, 1), dtype=np.int)
        y_peak = np.zeros((self.wavelength.size, 1), dtype=np.int)
        if fourier_mask is None:
            x_peak, y_peak = self.spectral_peak
            
            # Calculate mask radius. TODO: Update 250 to an automated guess based on input values.
            if self.rebin_factor != 1:
                mask_radius = 150./self.rebin_factor
            elif self.crop_fraction is not None and self.crop_fraction != 0:
                mask_radius = 150.*self.crop_fraction
            else:
                mask_radius = 150.
                mask = self.real_image_mask(x_peak, y_peak, mask_radius)
        else:
            #mask = np.asarray(fourier_mask, dtype=np.bool)
            mask = fourier_mask.mask
            for _ in range(len(fourier_mask.circle_list)):
                x_peak[_] = fourier_mask.circle_list[_].centery
                y_peak[_] = fourier_mask.circle_list[_].centerx

        #mask = np.atleast_3d(mask)

        # Calculate Fourier transform of impulse response function
        # SFF
        #G = self.fourier_trans_of_impulse_resp_func(np.atleast_1d([propagation_distance]*
        #                        self.wavelength.size).reshape((1,1,-1))-self.chromatic_shift)
        
        
        # Apodize the result
        if compute_digital_phase_mask:
            # Now calculate digital phase mask. First center the spectral peak for each channel
            x_peak, y_peak = x_peak.reshape(-1), y_peak.reshape(-1)
            shifted_ft_hologram = np.empty_like(np.atleast_3d(mask),dtype=COMPLEXDTYPE)
            for channel in range(self.wavelength.size):
                shifted_ft_hologram[:,:,channel] = arrshift(self.ft_hologram * mask[:,:,channel],
                                                        [-x_peak[channel], 
                                                         -y_peak[channel]],
                                                        axes = (0,1))
            psi_ = self.apodize(shifted_ft_hologram * self.G)
            digital_phase_mask = self.get_digital_phase_mask(psi_)
            # Reconstruct the image
            # fftshift is independent of channel
            psi = np.empty_like(np.atleast_3d(shifted_ft_hologram))
    
            for channel in range(psi.shape[2]):
                psi[:,:,channel] = arrshift(fftshift(fft2(self.apodize(self.hologram) * digital_phase_mask[:,:,channel] 
                                            ).astype(COMPLEXDTYPE)) * 
                                            mask[:,:,channel],
                                            [-x_peak[channel], 
                                             -y_peak[channel]],
                                            axes = (0,1))
            psi *= G
        else: 
            psi = np.empty_like(np.atleast_3d(mask),dtype=COMPLEXDTYPE)
            for channel in range(psi.shape[2]):
                #psi[:,:,channel] = arrshift(fftshift(fft2(self.apodize(self.hologram) 
                psi[:,:,channel] = arrshift(fftshift(fft2(self.hologram 
                                            )) * 
                                            mask[:,:,channel],
                                            [-x_peak[channel], 
                                             -y_peak[channel]],
                                            axes = (0,1))
            psi *= G


        ret = np.empty_like(np.atleast_3d(psi))
        for channel in range(ret.shape[2]):
            ret[:,:,channel] = fftshift(ifft2(psi[:,:,channel]))
        
        #return fftshift(ifft2(psi).astype(COMPLEXDTYPE))
        return ret

    def get_digital_phase_mask(self, psi):
        """
        Calculate the digital phase mask (i.e. reference wave), as in Colomb et al. 2006, Eqn. 26 [1]_.
        Fit for a second order polynomial, numerical parametric lens with least
        squares to remove tilt, spherical aberration.
        .. [1] http://www.ncbi.nlm.nih.gov/pubmed/16512526
        Parameters
        ----------
        psi : `~numpy.ndarray`
            The product of the Fourier transform of the hologram and the Fourier
            transform of impulse response function
        Returns
        -------
        phase_mask : `~numpy.ndarray`
            Digital phase mask, used for correcting phase aberrations.
        """
        start_time = time.time()
        inverse_psi = np.empty_like(psi)
        for channel in range(self.wavelength.size):
            inverse_psi[:,:,channel] = fftshift(ifft2(psi[:,:,channel]), axes = (0, 1))
        print("get_phase_mask: ET=%f"%(time.time()-start_time))

        #inverse_psi = fftshift(ifft2(psi).astype(COMPLEXDTYPE), axes = (0, 1))

        #unwrapped_phase_image = np.atleast_3d(unwrap_phase(inverse_psi))/2/self.wavenumber
        unwrapped_phase_image = np.atleast_3d(_unwrap_phase(inverse_psi))/2/self.wavenumber
        smooth_phase_image = gaussian_filter(unwrapped_phase_image, [50, 50, 0]) # do not filter along axis 2
        print("get_phase_mask: ET=%f"%(time.time()-start_time))

        high = np.percentile(unwrapped_phase_image, 99)
        low = np.percentile(unwrapped_phase_image, 1)
        print("get_phase_mask: ET=%f"%(time.time()-start_time))

        smooth_phase_image[high < unwrapped_phase_image] = high
        smooth_phase_image[low > unwrapped_phase_image] = low
        print("get_phase_mask: ET=%f"%(time.time()-start_time))

        # Fit the smoothed phase image with a 2nd order polynomial surface with
        # mixed terms using least-squares.
        # This is iterated over all wavelength channels separately
        # TODO: can this be done on the smooth_phase_image along axis 2 instead
        # of direct iteration?
        smooth_phase_image = smooth_phase_image
        channels = np.split(smooth_phase_image, smooth_phase_image.shape[2], axis = 2)
        fits = list()

        # Need to flip mgrid indices for this least squares solution
        y, x = self.mgrid - self.n/2
        x, y = np.squeeze(x), np.squeeze(y)
        print("get_phase_mask: ET=%f"%(time.time()-start_time))

        for channel in channels:
            v = np.array([np.ones(len(x[0, :])), x[0, :], y[:, 0], x[0, :]**2,
                        x[0, :] * y[:, 0], y[:, 0]**2])
            coefficients = np.linalg.lstsq(v.T, np.squeeze(channel))[0]
            fits.append(np.dot(v.T, coefficients))
        print("get_phase_mask: ET=%f"%(time.time()-start_time))
            
        field_curvature_mask = np.stack(fits, axis = 2)
        digital_phase_mask = np.exp(-1j*self.wavenumber * field_curvature_mask)
        print("get_phase_mask: ET=%f"%(time.time()-start_time))

        return digital_phase_mask

    def apodize(self, array, alpha=0.075):
        """
        Force the magnitude of an array to go to zero at the boundaries.
        Parameters
        ----------
        array : `~numpy.ndarray`
            Array to apodize
        alpha : float between zero and one
            Alpha parameter for the Tukey window function. For best results,
            keep between 0.075 and 0.2.
        Returns
        -------
        apodized_arr : `~numpy.ndarray`
            Apodized array
        """
        if self.apodization_window_function is None:
            x, y = self.mgrid
            n = len(x[0])
            tukey_window = tukey(n, alpha)
            self.apodization_window_function = np.atleast_3d(tukey_window[:, np.newaxis] * tukey_window)
        
        # In the most general case, array might represent a multi-wavelength hologram
        apodized_array = np.squeeze(np.atleast_3d(array) * self.apodization_window_function)
        return apodized_array
        
    def fourier_trans_of_impulse_resp_func(self, propagation_distance):
        """
        Calculate the Fourier transform of impulse response function, sometimes
        represented as ``G`` in the literature.
        For reference, see Eqn 3.22 of Schnars & Juptner (2002) Meas. Sci.
        Technol. 13 R85-R101 [1]_,
        .. [1] http://x-ray.ucsd.edu/mediawiki/images/d/df/Digital_recording_numerical_reconstruction.pdf
        Parameters
        ----------
        propagation_distance : float
            Propagation distance [m]
        Returns
        -------
        G : `~numpy.ndarray`
            Fourier transform of impulse response function
        """
        x, y = self.mgrid - self.n/2
        x, y = np.atleast_3d(x), np.atleast_3d(y)
        propagation_distance = np.atleast_3d(propagation_distance)

        #G = np.zeros((self.n, self.n, len(propagation_distance), len(self.wavelength)), dtype=COMPLEXDTYPE)
        #reconst.util.ComputeG_f(x, y, self.wavelength, propagation_distance, self.n, self.dx, self.dy, G)
        first_term = (self.wavelength**2 * (x + self.n**2 * self.dx**2 /
                      (2.0 * propagation_distance * self.wavelength))**2 /
                      (self.n**2 * self.dx**2))
        second_term = (self.wavelength**2 * (y + self.n**2 * self.dy**2 /
                       (2.0 * propagation_distance * self.wavelength))**2 /
                       (self.n**2 * self.dy**2))
        G = np.exp(-1j * self.wavenumber * propagation_distance *
                   np.sqrt(1.0 - first_term - second_term))
        return G
        
    def real_image_mask(self, center_x, center_y, radius):
        """
        Calculate the Fourier-space mask to isolate the real image
    
        Parameters
        ----------
        center_x : `~numpy.ndarray`
            ``x`` centroid [pixels] of real image in Fourier space for each 
            image in a stack.
        center_y : `~numpy.ndarray`
            ``y`` centroid [pixels] of real image in Fourier space for each
            image in a stack.
        radius : float
            Radial width of mask [pixels] to apply to the real image in Fourier
            space
    
        Returns
        -------
        mask : `~numpy.ndarray`
            Binary-valued mask centered on the real-image peak in the Fourier
            transform of the hologram.
        """
        center_x, center_y = np.reshape(center_x, (1, 1, -1)), np.reshape(center_y, (1, 1, -1))
        x, y = self.mgrid
        x, y = x[:,:,None], y[:,:,None]
        x_shift = x-center_x
        y_shift = y-center_y
        mask = np.zeros_like(np.atleast_3d(x_shift), dtype = np.bool)
        mask[(x_shift)**2 + (y_shift)**2 < radius**2] = True

        # exclude corners
        #buffer = 20
        #if self.crop_fraction is not None:
        #    buffer = buffer*self.crop_fraction
        #mask[((x_shift)**2 + (y_shift)**2) < buffer**2] = 0.0

        return mask
    
    def fourier_peak_centroid(self, gaussian_width=10):
        """
        Calculate the centroid of the signal spike in Fourier space near the
        frequencies of the real image.

        Parameters
        ----------
        fourier_arr : `~numpy.ndarray`
            Fourier-transform of the hologram
        margin_factor : int
            Fraction of the length of the Fourier-transform of the hologram
            to ignore near the edges, where spurious peaks occur there.

        Returns
        -------
        pixel : `~numpy.ndarray`
            Pixel at the centroid of the spike in Fourier transform of the
            hologram near the real image.
        """
        
        return _find_peak_centroid(np.abs(self.ft_hologram), self.wavelength, gaussian_width)
        
        
    def _reconstruct_multithread(self, propagation_distances, fourier_mask=None):
        """
        Reconstruct phase or intensity for multiple distances, for one hologram.
        Parameters
        ----------
        propagation_distances : `~numpy.ndarray` or list
            Propagation distances to reconstruct
        threads : int
            Number of threads to use via `~multiprocessing`
        fourier_mask : array_like or None, optional
            Fourier-domain mask. If None (default), a mask is determined from the position of the main
            spectral peak. If array_like, the array will be cast to boolean.
        Returns
        -------
        wave_cube : `~numpy.ndarray`, ndim 4
        """ 
        cube = np.empty(shape = self.hologram.shape + (self.wavelength.size, len(propagation_distances)),
                        dtype = COMPLEXDTYPE)
        with Pool(None) as pool:
            slices = pool.map( partial(self._reconstruct, fourier_mask = fourier_mask), propagation_distances)
        #for _ in range(len(self.propagation_distances)):
        #    self._reconstruct(
        
        cube = np.stack(slices, axis = 3)        
        return np.swapaxes(cube, 2, 3)
    
    def update_spectral_peak(self, spectral_peak):
        """
        Update spectral peak centroid values.
        
        Parameters
        ----------
        spectral_peak : `~numpy.ndarray`
            Centroid of spectral peak for wavelength in power spectrum of hologram FT 
            (len(self.wavelength) x 2)
        """
        
        spectral_peak = np.atleast_2d(spectral_peak)
        
        if spectral_peak.shape[1] != 2 or spectral_peak.shape[0] != self.wavelength.shape[2]:
            message = ("Spectral peak array must be of shape {0} by 2. "
                       "{0} is the number of wavelengths."
                       .format(self.wavelength.shape[2]))
            raise UpdateError(message)

        spectral_peak = spectral_peak.astype(int)
        
        self._spectral_peak = spectral_peak.swapaxes(0,1)
        
    def update_chromatic_shift(self,chromatic_shift):
        """
        Update chromatic shift values for changed depth of focus for different wavelengths.
        
        Parameters
        ----------
        spectral_peak : `~numpy.ndarray`
            1xN_wavelength list of depth of focus changes
        """
        if chromatic_shift is not None:

            chromatic_shift = np.atleast_1d(chromatic_shift).reshape((1,1,-1)).astype(FLOATDTYPE)
            if chromatic_shift.shape[2] != self.wavelength.shape[2]:
                message = ("Chromatic shift must be of length {0} (number of wavelengths)."
                            .format(self.wavelength.shape[2]))
                raise UpdateError(message)
            
        self._chromatic_shift = chromatic_shift

    #SFF
    def update_G_factor (self, propagation_distance):

        wavelength = np.atleast_1d(self.wavelength).reshape(1,1,-1).astype(FLOATDTYPE)
        propagation_distance = np.atleast_1d(propagation_distance).reshape(1,1,-1).astype(FLOATDTYPE)

        #reconst_util.ComputeG_f(x, y, np.squeeze(self.wavelength), np.squeeze(propagation_distance-chromatic_shift), self.n, self.dx, self.dy, self.G)
        self.G = compute_G_factor(propagation_distance, self.n, self.dx, self.dy, wavelength, old_implementation=True)

#        self.G = np.zeros((self.n, self.n, propagation_distance.size, self.wavelength.size), dtype=COMPLEXDTYPE)
#        x, y =  np.mgrid[0:self.n, 0:self.n].astype(FLOATDTYPE) - self.n/2
#        for li in range(wavelength.size):
#            wvl = wavelength[0,0,li]
#            for di in range(propagation_distance.size):
#                d = propagation_distance[0,0,di]
#                ### Old solution
#                #first_term =  (wvl**2.0 * (x + self.n**2. * self.dx**2./(2.0 * d * wvl))**2 / (self.n**2. * self.dx**2.))
#                #second_term = (wvl**2.0 * (y + self.n**2. * self.dy**2./(2.0 * d * wvl))**2 / (self.n**2. * self.dy**2.))
#                #self.G[:,:,di,li] = np.exp(-1j * 2.* np.pi * (d / wvl) * np.sqrt(1. - first_term - second_term))
#
#                ### Move the 'd' out to avoid divide by zero
#                first_term =  (wvl**2.0 * (d * x + self.n**2. * self.dx**2./(2.0 * wvl))**2 / (self.n**2. * self.dx**2.))
#                second_term = (wvl**2.0 * (d * y + self.n**2. * self.dy**2./(2.0 * wvl))**2 / (self.n**2. * self.dy**2.))
#                self.G[:,:,di,li] = np.exp(-1j * 2.* np.pi / wvl * np.sign(d) * np.sqrt(d**2. - first_term - second_term))

    def set_G_factor (self, G_factor_array):
        
        ### TODO:  Place restrictions
        self.G = G_factor_array

def unwrap_phase(reconstructed_wave, wavelength=None):
    if wavelength is not None and wavelength.size == 3:
        #return _unwrap_phase_multiwavelength(reconstructed_wave, wavelength.reshape(-1))
        ret = np.zeros_like(reconstructed_wave, dtype=COMPLEXDTYPE)
        for l in range(len(wavelength)):
            ret[:,:,:,l] = _unwrap_phase(reconstructed_wave[:,:,:,l])
        return ret
    else:
        return np.expand_dims(_unwrap_phase(reconstructed_wave), axis=3)

def _unwrap_phase(reconstructed_wave, seed=RANDOM_SEED):
    """
    2D phase unwrap a complex reconstructed wave.
    Essentially a wrapper around the `~skimage.restoration.unwrap_phase`
    function.
    Parameters
    ----------
    reconstructed_wave : `~numpy.ndarray`
        Complex reconstructed wave
    seed : float (optional)
        Random seed, optional.
    Returns
    -------
    `~numpy.ndarray`
        Unwrapped phase image
    """   
    phase = 2 * np.arctan(reconstructed_wave.imag / reconstructed_wave.real)
    # No channel, no need for shenanigans
    if phase.ndim < 3:
        return skimage_unwrap_phase(phase, seed=seed).astype(FLOATDTYPE)

    # Each wavelength channel must be done separately
    unwrapped = np.empty_like(reconstructed_wave)
    unwrapped_channels = list()
    for phase_channel in np.dsplit(phase, phase.shape[2]):
        unwrapped_channels.append( skimage_unwrap_phase(np.squeeze(phase_channel),seed=seed).astype(FLOATDTYPE))
    return np.dstack(unwrapped_channels)
    
def _unwrap_phase_multiwavelength(reconstructed_wave, wavelength):
    """
    Perform multi-wavelength phase unwrapping.

    For reference, see N. Warnasooriya and M. K. Kim, Opt. Express 15, 9239-9247 (2007)

    .. [3] https://www.osapublishing.org/oe/fulltext.cfm?uri=oe-15-15-9239&id=139880

    Parameters
    ----------
    reconstructed_wave : `~numpy.ndarray`
        Complex reconstructed wave

    Returns
    -------
    `~numpy.ndarray`
        Unwrapped phase image
    """
    
    # TODO: Add 2-wavelength phase unwrapping.

    # Due to previous implementation
    # We must have the dimensions be (X,Y, wavelengths, Z) in this function
    reconstructed_wave = np.swapaxes(reconstructed_wave, 2, 3)
    
    # Get the phase maps 
    # np.arctan2 returns in the range (-pi,pi) so we shift to (0, 2*pi)
    #phase = np.squeeze(np.arctan2(reconstructed_wave.imag, reconstructed_wave.real) + np.pi)
    phase = np.arctan2(reconstructed_wave.imag, reconstructed_wave.real) + np.pi

    # Get the beat wavelengths
    w1,w2,w3 = tuple(wavelength)

    lambda_13 = w1*w3/np.abs(w1-w3)
    lambda_23 =w1*w2/np.abs(w1-w2)
    lambda_1323 = lambda_13*lambda_23/np.abs(lambda_13-lambda_23)

    # Get the coarse maps
    #coarse_13 = phase[:,:,0]-phase[:,:,2]
    coarse_13 = phase[:,:,0,:]-phase[:,:,2,:]
    #coarse_23 = phase[:,:,1]-phase[:,:,2]
    coarse_23 = phase[:,:,1,:]-phase[:,:,2,:]
    coarse_13[coarse_13<0] = coarse_13[coarse_13<0] + 2*np.pi
    coarse_23[coarse_23<0] = coarse_23[coarse_23<0] + 2*np.pi
    coarse_1323 = coarse_13 - coarse_23
    coarse_1323[coarse_1323<0] = coarse_1323[coarse_1323<0] + 2*np.pi

    # Get the surface profiles
    z_13 = lambda_13*coarse_13/(2*np.pi)
    z_23 = lambda_23*coarse_23/(2*np.pi)
    z_1323 = lambda_1323*coarse_1323/(2*np.pi)

    # Get the integer surface profile for maximum beat wavelength
    z_a = np.rint(z_1323/lambda_13)*lambda_13
    z_b = z_a + z_13
    z_c = z_1323 - z_b
    z_d = z_c
    z_d[z_c[:] > lambda_13/2] = z_c[z_c[:] > lambda_13/2] + lambda_13.reshape(-1)
    z_d[z_c[:] < -lambda_13/2] = z_c[z_c[:] < -lambda_13/2] - lambda_13.reshape(-1)
    
    # Get surface profiles for individual wavelength
    z = np.expand_dims(wavelength, axis = 3)*phase/(2*np.pi)
    #z = np.expand_dims(wavelength, axis = 3)[:,0]*phase/(2*np.pi)
    
    #for channel in range(z.shape[2]):
    #    z[:,:,channel] = wavelength[:,:,channel]*phase[:,:,channel]/(2*np.pi)
    z_e = np.empty_like(z)
    for channel in range(z_e.shape[2]):
        z_e[:,:,channel] = np.rint(z_d/wavelength[channel])*wavelength[channel]
    z_f = z_e+z
    z_g = np.empty_like(z_f)
    for channel in range(z_g.shape[2]):
        z_g[:,:,channel] = z_d-z_f[:,:,channel]
    for channel in range(z_g.shape[2]):
        z_f_curr = z_f[:,:,channel]
        z_g_curr = z_g[:,:,channel]
        z_g_curr[z_f_curr[:] > wavelength[channel]/2] = z_f_curr[z_f_curr[:] > wavelength[channel]/2] + wavelength[channel]
        z_g_curr[z_f_curr[:] < -wavelength[channel]/2] = z_f_curr[z_f_curr[:] < -wavelength[channel]/2] - wavelength[channel]
        z_g[:,:,channel] = z_g_curr
    #return np.swapaxes(z_g*2*np.pi/np.expand_dims(wavelength, axis = 3)[:,0], 2, 2)    # Back to (X, Y, Z, wavelengths)
    ret = np.swapaxes(z_g*2*np.pi/np.expand_dims(wavelength, axis = 3), 2, 3) # Back to (X, Y, Z, wavelengths)
    return ret    


class ReconstructedWave(object):
    """
    Container for reconstructed waves and their intensity and phase
    arrays.
    """
    def __init__(self, reconstructed_wave, fourier_mask, wavelength, depths):
        """
        Parameters
        ----------
        reconstructed_wave : array_like, complex
            Reconstructed wave. Last axis is wavelength channel. 
        fourier_mask : array_like
            Reconstruction Fourier mask, in 2- or 3- dimensions.
        wavelength : float or array_like
            Wavelength(s) of the reconstructed wave.
        depths : array_like
            Reconstruction depths, corresponding to each slice of `reconstructed_wave` along
            axis 2.
        """
        self.reconstructed_wave = reconstructed_wave
        self.depths = np.atleast_1d(depths)
        self._amplitude_image = None
        self._intensity_image = None
        self._phase_image = None
        self.fourier_mask = np.asarray(fourier_mask, dtype = np.bool)
        self.wavelength = np.atleast_1d(wavelength)
        self.random_seed = RANDOM_SEED
    
    @property
    def intensity(self):
        """
        `~numpy.ndarray` of the reconstructed intensity
        """
        if self._intensity_image is None:
            self._intensity_image = self.amplitude ** 2

        return self._intensity_image

    @property
    def amplitude(self):
        """
        `~numpy.ndarray` of the reconstructed amplitude
        """
        if self._amplitude_image is None:
            self._amplitude_image = np.abs(self.reconstructed_wave)

        return self._amplitude_image

    @property
    def phase(self):
        """
        `~numpy.ndarray` of the reconstructed, unwrapped phase.

        Returns the unwrapped phase using `~skimage.restoration.unwrap_phase`.
        """
        if self._phase_image is None:
            self._phase_image = unwrap_phase(self.reconstructed_wave, self.wavelength)

        return self._phase_image

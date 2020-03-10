"""
###############################################################################
#  Copyright 2019, by the California Institute of Technology. ALL RIGHTS RESERVED.
#  United States Government Sponsorship acknowledged. Any commercial use must be
#  negotiated with the Office of Technology Transfer at the
#  California Institute of Technology.
#
#  This software may be subject to U.S. export control laws. By accepting this software,
#  the user agrees to comply with all applicable U.S. export laws and regulations.
#  User has the responsibility to obtain export licenses, or other export authority
#  as may be required before exporting such information to foreign countries or providing
#  access to foreign persons.
#
#  file:	shampoo_lite/reconstruction.py
#  author:	S. Felipe Fregoso
#  description:	Module containing reconstruction algorithms
#               This module was named after Brett Morris' version SHAMPOO
#               but many of the algorithms there were not adequate and
#               were redone for our purposes
#
###############################################################################
"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

#import datatypes
from .datatypes import (BOOLDTYPE, FLOATDTYPE, COMPLEXDTYPE, FRAMEDIMENSIONS, NUMFFTTHREADS)

#import fftutils
from .fftutils import (fftshift, fft2, ifft2, fft3, ifft3, FFT_3)

#from shampoo_lite.mask import(Circle, Mask)

###########################################################
###              Constants
###########################################################
RANDOM_SEED = 42

def reshape_to_3d(array, dtype):
    """
    Gets input array and reshapes is to be an array of
    3 dimensions where the first two dimensions are 1
    and the other is the size of the array

    Example:  array = [1, 2, 3]
    Output:  out.shape => (1, 1, 3)
    """
    return np.atleast_1d(array).reshape((1, 1, -1)).astype(dtype)

###########################################################
###              Classes
###########################################################
class Hologram():
    """
    Container for holograms and methods to reconstruct them.
    """
    def __init__(self, hologram, crop_fraction=None, wavelength=405e-3,
                 rebin_factor=1, pix_dx=3.45, pix_dy=3.45, system_magnification=1.0,
                 mask=None, apodize=True):
        """
        Constructor
        """
        self._crop_fraction = crop_fraction
        self._rebin_factor = rebin_factor
        self._system_magnification = system_magnification
        self._random_seed = RANDOM_SEED
        self.mask = mask
        self.hologram = None
        self.hololen = None
        self.wavelength = None
        self.wavenumber = None
        self._pix_width_x = None
        self._pix_width_y = None
        self._spectral_peak = None
        self._chromatic_shift = None
        self.apodization_window_function = None
        self._ft_hologram = None
        self._apodize_mask = None
        self._angular_spec_hologram = None
        self._mgrid = None
        self._f_mgrid = None
        self._propagation_array = None
        self.G = None
        self.x_peak = None
        self.y_peak = None

        self.set_hologram(hologram)

        self.set_wavelength(wavelength)

        self.set_pixel_width(pix_dx, pix_dy)

        self._apodized_hologram = self.hologram * self.apodize_mask()

        self.update_ft_hologram(apodize=apodize)
#        if self.wavelength.size != FRAMEDIMENSIONS[2] or self.hololen != FRAMEDIMENSIONS[1]:
#            #print("$$$$$$$$ Adjusted FFT $$$$$$$$$$$")
#            datatypes.FRAMEDIMENSIONS = (self.hololen, self.hololen, self.wavelength.size)
#            #print("Updating FFT shape", FRAMEDIMENSIONS)
#            myFFT3 = FFT_3(FRAMEDIMENSIONS, FLOATDTYPE, COMPLEXDTYPE, threads=NUMFFTTHREADS)
#            fftutils.fft3 = myFFT3.fft3
#            fftutils.ifft3 = myFFT3.ifft3
#            fftutils.fft2 = myFFT3.fft2
#            fftutils.ifft2 = myFFT3.ifft2

    def set_hologram(self, hologram):
        """
        Sets the hologram image and validates it
        """
        hologram = np.asarray(hologram, dtype=FLOATDTYPE)
        if hologram.ndim != 2:
            raise ValueError('Hologram dimensions ({}) are invalid. Holograms'\
                             'should be 2D image'.format(hologram.shape))

        self._crop_and_rebin(hologram)
        self.hololen = self.hologram.shape[0]

    def get_hologram(self):
        """
        Return the raw image hologram
        """
        return self.hologram

    def update_ft_hologram(self, apodize=False):
        """
        Update the FFT of the hologram
        """
        if apodize==True:
            #apodized_hologram = self.apodize(self.hologram)
            self._ft_hologram = fftshift(fft2(self._apodized_hologram))
        else:
            self._ft_hologram = fftshift(fft2(self.hologram))

        return self._ft_hologram

    def get_ft_hologram(self, apodize=False):
        """
        Return the FT of hologram
        """
        if not self._ft_hologram:
           self.update_ft_hologram(apodize=apodize)

        return self._ft_hologram

    def update_hologram(self, hologram, crop_fraction=None,
                        wavelength=None, rebin_factor=None,
                        pix_dx=None, pix_dy=None,
                        mask=None):
        """
        Update the object based on inputs
        This avoids creating a new hologram object
        """
        if not crop_fraction:
            self._crop_fraction = crop_fraction
        if not rebin_factor:
            self._rebin_factor = rebin_factor

        self.set_hologram(hologram)

        if not wavelength:
            self.set_wavelength(wavelength)

        self.set_pixel_width(pix_dx, pix_dy)

        self._ft_hologram = None;

#        global FRAMEDIMENSIONS
#        global myFFT3
#        global fft3
#        global ifft3
#        global fft2
#        global ifft2
#        if self.wavelength.size != FRAMEDIMENSIONS[2] or self.hololen != FRAMEDIMENSIONS[1]:
#            global myFFT3, fft3, ifft3, fft2, ifft2
#            #print("$$$$$$$$ Adjusted FFT $$$$$$$$$$$")
#            #print("wavelength.size, self.hololen, FRAMEDDIMENSIONS[2]: ", self.wavelength.size, self.hololen, FRAMEDIMENSIONS[2])
#            FRAMEDIMENSIONS = (self.hololen, self.hololen, self.wavelength.size)
#            #print("Updating FFT shape", FRAMEDIMENSIONS)
#            myFFT3 = FFT_3(FRAMEDIMENSIONS, FLOATDTYPE, COMPLEXDTYPE, threads=NUMFFTTHREADS)
#            fft3 = myFFT3.fft3
#            ifft3 = myFFT3.ifft3
#            fft2 = myFFT3.fft2
#            ifft2 = myFFT3.ifft2
#            self._mgrid = None
#            self.mgrid

    def _crop_and_rebin(self, hologram):
        """
        Crop and rebin input hologram
        """
        square_hologram = _crop_to_square(hologram)
        binned_hologram = _rebin_image(square_hologram, self._rebin_factor)

        # Crop the hologram by factor crop_factor, centered on original center
        if self._crop_fraction is not None:
            self.hologram = _crop_image(binned_hologram, self._crop_fraction)
        else:
            self.hologram = binned_hologram

    def set_wavelength(self, wavelength):
        """
        Set the wavelength and affected parameters
        """
        self.wavelength = reshape_to_3d(wavelength, FLOATDTYPE)
        self.wavenumber = 2 * np.pi / self.wavelength

    def set_pixel_width(self, pix_dx, pix_dy):
        """
        Set the pixel width based on input deltas
        """
        if pix_dx:
            self._pix_width_x = pix_dx/self._system_magnification * self._rebin_factor
        if pix_dy:
            self._pix_width_y = pix_dy/self._system_magnification * self._rebin_factor

        self.dk = 2*np.pi/(self.hololen * self._pix_width_x)

    @property
    def propagation_array(self):
        if self._propagation_array is None:
            k0 = reshape_to_3d(self.wavenumber, FLOATDTYPE)
            self._propagation_array = np.zeros((self.hololen, self.hololen, self.wavenumber.size), dtype=FLOATDTYPE)

            for i in range(k0.size):
                k = k0[0, 0, i]
                self._propagation_array[:, :, i] = np.sqrt(k**2 - (self.f_mgrid[0]**2 + self.f_mgrid[1]**2) * circ_prop(self.f_mgrid[0], self.f_mgrid[1], k))

        return self._propagation_array

    @property
    def mgrid(self):
        if self._mgrid is None:
            self._mgrid = np.meshgrid(np.arange(0, self.hololen), np.arange(0, self.hololen)) # meshgrid of pixels, useful for indexing

        return self._mgrid

    @property
    def f_mgrid(self):
        """ Frequency Coordinates MGrid"""
        if self._f_mgrid is None:
            kx = np.arange(-self.hololen/2, self.hololen/2) * self.dk
            ky = np.arange(-self.hololen/2, self.hololen/2) * self.dk
            self._f_mgrid = np.meshgrid(kx, ky) # meshgrid of pixels, useful for indexing

        return self._f_mgrid

    def apodize_mask(self):
        if self._apodize_mask is None:
            self._apodize_mask = np.cos((self.mgrid[0]-self.hololen/2)/self.hololen*np.pi)**0.25 * np.cos((self.mgrid[1]-self.hololen/2)/self.hololen*np.pi)**0.25

        return self._apodize_mask

    @property
    def angular_spectrum(self, apodize=True):

        if apodize:
            self._angular_spec_hologram = fftshift(fft2(fftshift(self._apodized_hologram)) * self._pix_width_x*self._pix_width_y/(2*np.pi))
        else:
            self._angular_spec_hologram = fftshift(fft2(fftshift(self.hologram)) * self._pix_width_x*self._pix_width_y/(2*np.pi))

        return self._angular_spec_hologram

    @property
    def spectral_peak(self):
        if self._spectral_peak is None:
            # Guess 'em
            self.update_spectral_peak(self.fourier_peak_centroid())

        return self._spectral_peak

    def spectral_mask(self, center_x_pix, center_y_pix, radius_pix):
        """ Spectral Mask in frequency coordinates"""
        kx = np.arange(-self.hololen/2, self.hololen/2) * self.dk
        ky = np.arange(-self.hololen/2, self.hololen/2) * self.dk
        centerX = kx[center_x_pix] # um^-1 frequency coordinate
        centerY = ky[center_y_pix] # um^-1
        radius = radius_pix * self.dk # um^-1
        spectralMask = (circ_prop(self.f_mgrid[0]-centerX, self.f_mgrid[1]-centerY, radius) > 0.5)
        spectralMask_centered = (circ_prop(self.f_mgrid[0], self.f_mgrid[1], radius) > 0.5)

        return (spectralMask, spectralMask_centered)

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
        x, y = x[:, :, None], y[:, :, None]
        x_shift = x-center_x
        y_shift = y-center_y
        mask = np.zeros_like(np.atleast_3d(x_shift), dtype=BOOLDTYPE)
        mask[(x_shift)**2 + (y_shift)**2 < radius**2] = True

        return mask


    def propagation_kernel(self, propagation_distance, spectralMask_centered):
        """
        Compute and return propagation kernel
        """

        propKernel = np.zeros((self.hololen, self.hololen, self.wavelength.size)) * 1j

        for i, wvl in enumerate(self.wavelength):
            propKernel[spectralMask_centered, i] = np.exp(1j*propagation_distance*self.propagation_array[spectralMask_centered, i])

        return propKernel

    ###################################################################3
    ###              Reconstruction
    ###################################################################3
    def reconstruct(self, propagation_distance, compute_spectral_peak=False, compute_digital_phase_mask=False, digital_phase_mask=None, fourier_mask=None, chromatic_shift=None, G_factor=None):

        propagation_distance = reshape_to_3d(propagation_distance, FLOATDTYPE)

        if chromatic_shift is not None:
            self.update_chromatic_shift(chromatic_shift)

        ang_spec = holo.angular_spectrum

        if not compute_spectral_peak:
            # Spectral Mask, in frequency coordinates
            coor = [(1389, 455, 250), (674, 1625, 250), (1267, 1497, 250)]

            spectralMask = np.zeros((self.hololen, self.hololen, self.wavelength.size), dtype=BOOLDTYPE)
            spectralMask_centered = np.zeros((self.hololen, self.hololen, self.wavelength.size), dtype=BOOLDTYPE)

            for i in range(self.wavelength.size):
                centerX_pix, centerY_pix, radius_pix = coor[i]
                spectralMask[:, :, i], spectralMask_centered[:, :, i] = self.spectral_mask(centerX_pix, centerY_pix, radius_pix)

            self.mask = spectralMask


        wave = np.zeros((self.hololen, self.hololen, propagation_distance.size, self.wavelength.size), dtype=ang_spec.dtype)

        for i in range(self.wavelength.size):

            propKernel = self.propagation_kernel(propagation_distance[0, 0, 0], spectralMask_centered[:, :, i])
            print(propKernel.shape)

            maskedHolo = np.roll(ang_spec*spectralMask[:, :, i], (int(self.hololen/2 - centerY_pix), int(self.hololen/2 - centerX_pix)), axis=(0, 1))

            proppedWave = propKernel[:, :, 0] * maskedHolo
            wave[:, :, 0, i] = fftshift(ifft2(fftshift(proppedWave))) * (self.hololen*self.dk * self.hololen*self.dk)/(2*np.pi)

            #reconField = np.fft.ifftshift(ifft2(np.fft.ifftshift(proppedWave))) * (self.hololen*self.dk * self.hololen*self.dk)/(2*np.pi)

            # Energy conservation
            spectralMaskNumber = np.sum(spectralMask**2)
            print(spectralMaskNumber)

#            E_image = np.sum(self._apodized_hologram * np.conj(self._apodized_hologram)) * self._pix_width_x*self._pix_width_y
#            E_fft = np.sum(ang_spec * np.conj(ang_spec)) * self.dk**2
#            E_maskedFFT = np.sum(maskedHolo * np.conj(maskedHolo)) * self.dk**2
#            E_reconstruction = np.sum(reconField * np.conj(reconField)) * self._pix_width_x*self._pix_width_y
#            print('E_image', E_image)
#            print('E_fft', E_fft)
#            print('E_maskedFFT', E_maskedFFT)
#            print('E_reconstruction', E_reconstruction)


        return ReconstructedWave(reconstructed_wave=wave, fourier_mask=self.mask,
                                 wavelength=self.wavelength, depths=propagation_distance)

class ReconstructedWave():
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
        self.fourier_mask = np.asarray(fourier_mask, dtype=BOOLDTYPE)
        self.wavelength = np.atleast_1d(wavelength)
        self._random_seed = RANDOM_SEED

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
            self._amplitude_image = self.reconstructed_wave*np.conj(self.reconstructed_wave)

        return self._amplitude_image

    @property
    def phase(self):
        """
        `~numpy.ndarray` of the reconstructed, unwrapped phase.

        Returns the unwrapped phase using `~skimage.restoration.unwrap_phase`.
        """
        if self._phase_image is None:
            self._phase_image = np.angle(self.reconstructed_wave)

        return self._phase_image

###################################################################3
###              Support Functions
###################################################################3
def _crop_to_square(image, two_pwr_dim_len_square_up=True):
    """
    Ensure that hologram is square.

    two_pwr_dim_len_square_up:  True it will reshape to largest dimension, else to smallest dimension
    """
    import math

    sh = image.shape

    if sh[0] == sh[1]:
        square_image = image
    else:
        if two_pwr_dim_len_square_up:
            dim_len = 2 ** int(math.log(max(sh), 2))
            square_image = np.zeros((dim_len, dim_len), dtype=image.dtype)
            temp_sh = (sh[0] if dim_len > sh[0] else dim_len, sh[1] if dim_len > sh[1] else dim_len)
            #print(temp_sh)
            square_image[:temp_sh[0], :temp_sh[1]] = image[:temp_sh[0], :temp_sh[1]]
        else:
            square_image = image[:min(sh), :min(sh)]

    return square_image

def _rebin_image(a, binning_factor):
    # Courtesy of J.F. Sebastian: http://stackoverflow.com/a/8090605
    if binning_factor == 1:
        return a

    new_shape = (a.shape[0]/binning_factor, a.shape[1]/binning_factor)
    sh = (new_shape[0], a.shape[0]//new_shape[0], new_shape[1],
          a.shape[1]//new_shape[1])
    return a.reshape(map(int, sh)).mean(-1).mean(1)

def circ_prop(kx, ky, k):

    r = np.sqrt(kx**2+ky**2)/k
    z = r < 1

    return z.astype(np.float)


if __name__ == "__main__":
    #from skimage.io import imread
    import time

    showFigs = True

    #im = imread('../data/USAF_multi.tif')
    im = mpimg.imread('../data/USAF_multi.tif')
    #im = imread('../data/Hologram.tif')

    propagation_distance = 370 #um
    wvl = [405e-3, 532e-3, 605e-3] #Wavelength um
    m = 10 #System magnification
    p = 3.45 #um, pixel size (image space)
    dx = p/m

    start_time = time.time()
    holo = Hologram(im, wavelength=wvl,
                    pix_dx=p, pix_dy=p, system_magnification=m)
    print("Elapsed Time: ", time.time()-start_time)

    ang_spec = holo.angular_spectrum

    start_time = time.time()
    wave = holo.reconstruct(propagation_distance)
    reconAmplitude = wave.amplitude
    reconPhase = wave.phase
    print("Elapsed Time: ", time.time()-start_time)

#
#        if showFigs:
#            x = np.arange(-holo.n/2,holo.n/2) * holo.dx # Object space x and y vectors
#            y = np.arange(-holo.n/2,holo.n/2) * holo.dy
#
#            dk = 2*np.pi/(holo.n*holo.dx)
#            kx = np.arange(-holo.n/2,holo.n/2) * dk
#            ky = np.arange(-holo.n/2,holo.n/2) * dk
#
#            # Plot the results
#            plt.figure(1)
#            plt.imshow(holo.hologram, extent=[x[0], x[-1], y[0], y[-1]], aspect=1, cmap='gray')
#            plt.xlabel('Object Space, um')
#            plt.title('Raw Hologram - US Air Force Resolution Target')
#            #plt.show()
#
#            plt.figure(2)
#            #plt.imshow( np.log10(np.real((ang_spec*(spectralMask+0.1))*np.conj(ang_spec*(spectralMask+0.1)))) , extent=[kx[0],kx[-1],ky[0],ky[-1]], aspect=1, cmap='gray')
#            plt.imshow( np.log10(np.real((ang_spec*(spectralMask+0.1))*np.conj(ang_spec*(spectralMask+0.1)))) , aspect=1, cmap='gray')
#            plt.xlabel('Frequency Space, um^-1')
#            plt.title('Angular Spectrum - Showing Masked Region')
#            #plt.show()
#
#            plt.figure(6)
#            plt.imshow(np.real(reconAmplitude), extent=[x[0],x[-1],y[0],y[-1]], aspect=1, cmap='gray')
#            plt.xlabel('Object Space, um')
#            plt.title('Reconstructed Intensity')
#            #plt.show()
#
#            plt.figure(7)
#            plt.imshow(reconPhase, extent=[x[0],x[-1],y[0],y[-1]], aspect=1, cmap='hsv')
#            plt.xlabel('Object Space, um')
#            plt.title('Reconstructed Phase')
#            plt.colorbar()
#            plt.show()



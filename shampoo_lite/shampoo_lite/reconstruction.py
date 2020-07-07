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

from .datatypes import (BOOLDTYPE, FLOATDTYPE, COMPLEXDTYPE, FRAMEDIMENSIONS, NUMFFTTHREADS)

from .fftutils import (fftshift, fft2, ifft2, fft3, ifft3, FFT_3)

# Used for spectral peak computation
from scipy.ndimage import gaussian_filter, maximum_filter

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
###########################################################
###              Classes
###########################################################
class Hologram():
    """
    Container for holograms and methods to reconstruct them.
    """
    def __init__(self, hologram, crop_fraction=None, wavelength=405e-3,
                 rebin_factor=1, pix_dx=3.45, pix_dy=3.45, system_magnification=1.0,
                 fourier_mask=None, apodize=True):
        """
        Constructor

        Parameters
        ----------
        hologram : 2D np.array
            Image array which is the hologram
        crop_fraction : float or None
            TBD
        wavelength : float or np.array
            Wavelength in units of um
        rebin_factor : float
            TBD
        pix_dx : float
            Pixel size (image space) in X dimension
        pix_dy : float
            Pixel size (image space) in Y dimension
        system_magnification : float
            Magnficiation of the system
        mask : TBD or None
            TBD
        apodize : bool
            Apply apodize mask to hologram if TRUE, else FALSE
        """
        self._crop_fraction = crop_fraction
        self._rebin_factor = rebin_factor
        self._system_magnification = system_magnification
        self._random_seed = RANDOM_SEED
        if fourier_mask:
            self.spectral_mask_uncentered = fourier_mask[0]
            self.spectral_mask_centered = fourier_mask[1]
        else:
            self.spectral_mask_uncentered = None
            self.spectral_mask_centered = None
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

        Parameters
        ----------
        hologram : 2D np.array
            Image hologram
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

    @property
    def ft_hologram(self, apodize=False):
        """
        Return the FT of hologram

        If internal ft_hologram exists, then return that, else
        compute recompute fourier transform and update.
        """
        if self._ft_hologram is None:

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

        Parameters
        -----------
        pix_dx : float
            Pixel size in X dimension in image space
        pix_dy : float
            Pixel size in Y dimension in image space
        """
        if pix_dx:
            effective_pixel_size = pix_dx/self._system_magnification # object space
            self._pix_width_x = effective_pixel_size * self._rebin_factor
        if pix_dy:
            effective_pixel_size = pix_dy/self._system_magnification # object space
            self._pix_width_y =  effective_pixel_size * self._rebin_factor

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

    @property
    def spectral_peak(self):
        if self._spectral_peak is None:
            # Guess 'em
            self.update_spectral_peak(self.fourier_peak_centroid())

        return self._spectral_peak

    def spectral_mask(self, center_x_pix, center_y_pix, radius_pix):
        """ 
        Compute spectral mask in frequency coordinates
        
        Two arrays are computed, the first a circular spectral mask where only the pixels within
        the mask are '1' and all else is '0'.  The other array is the same spectral mask
        but centered.

        Parameters
        ----------
        center_x_pix : float
            X coordinate in pixels of max spectral peak 
            This should be the center location of a fourier satellite
        center_y_pix : float
            Y coordinate in pixels of max spectral peak 
            This should be the center location of a fourier satellite
        radius_pix : float
            Radius of satellite in pixels

        Return : tuple of 2 np.array
            (spectral_mask, spectral_mask_centered)
        """
        kx = np.arange(-self.hololen/2, self.hololen/2) * self.dk
        ky = np.arange(-self.hololen/2, self.hololen/2) * self.dk
        centerX = kx[center_x_pix] # um^-1 frequency coordinate
        centerY = ky[center_y_pix] # um^-1
        radius = radius_pix * self.dk # um^-1
        spectral_mask_uncentered = (circ_prop(self.f_mgrid[0]-centerX, self.f_mgrid[1]-centerY, radius) > 0.5)
        spectral_mask_centered = (circ_prop(self.f_mgrid[0], self.f_mgrid[1], radius) > 0.5)

        return (spectral_mask_uncentered, spectral_mask_centered,)

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


    def propagation_kernel(self, propagation_distance, spectral_mask_centered):
        """
        Compute and return propagation kernel
        """

        propKernel = np.zeros((self.hololen, self.hololen, self.wavelength.size)) * 1j

        for i, wvl in enumerate(self.wavelength):
            propKernel[spectral_mask_centered, i] = np.exp(1j*propagation_distance*self.propagation_array[spectral_mask_centered, i])

        return propKernel

    ###################################################################3
    ###              Reconstruction
    ###################################################################3
    def reconstruct(self, propagation_distance, compute_spectral_peak=False, compute_digital_phase_mask=False, digital_phase_mask=None, fourier_mask=None, chromatic_shift=None, G_factor=None):
        """
        Parameters
        -----------
        propagation_distance : float or np.array of floats
            TBD
        compute_spectral_peak : boolean
            If TRUE then mathematically find the peak of the fourier image for each wavelength and create spectral mask.
            If FALSE then input mask 'fourier_mask' must be used
        
        """

        propagation_distance = reshape_to_3d(propagation_distance, FLOATDTYPE)

        if chromatic_shift is not None:
            self.update_chromatic_shift(chromatic_shift)

        ang_spec = self.angular_spectrum

        if compute_spectral_peak:
            # Find location of all spectral peaks per wavelength. These are the center of the fourier mask
            spectral_peak_loc= self.spectral_peak

            # Create empty spectral mask
            spectral_mask_uncentered = np.zeros((self.hololen, self.hololen, self.wavelength.size), dtype=BOOLDTYPE)
            spectral_mask_centered = np.zeros((self.hololen, self.hololen, self.wavelength.size), dtype=BOOLDTYPE)
            spectral_mask_coordinates = []

            # populate spectral mask
            for i in range(self.wavelength.size):

                #center_x_pix, center_y_pix, radius_pix = (spectral_peak_loc[1][i], spectral_peak_loc[0][i], 250) #coor[i]
                spectral_mask_coordinates.append((spectral_peak_loc[1][i], spectral_peak_loc[0][i], 250)) #coor[i]
                spectral_mask_uncentered[:, :, i], spectral_mask_centered[:, :, i] = self.spectral_mask(spectral_mask_coordinates[i][0], spectral_mask_coordinates[i][1], spectral_mask_coordinates[i][2])

            self.spectral_mask_uncentered = spectral_mask_uncentered
            self.spectral_mask_centered = spectral_mask_centered
        else:
            pass

        wave = np.zeros((self.hololen, self.hololen, propagation_distance.size, self.wavelength.size), dtype=ang_spec.dtype)

        for i in range(self.wavelength.size):

            dist_idx = 0 # because we going to process a single propagation distance only
            print("propagation distance: ", propagation_distance[0, 0, dist_idx])
            propKernel = self.propagation_kernel(propagation_distance[0, 0, dist_idx], self.spectral_mask_centered[:, :, i])

            maskedHolo = np.roll(ang_spec * self.spectral_mask_uncentered[:, :, i], (int(self.hololen/2 - spectral_mask_coordinates[i][1]), int(self.hololen/2 - spectral_mask_coordinates[i][0])), axis=(0, 1))

            proppedWave = propKernel[:, :, dist_idx] * maskedHolo
            wave[:, :, dist_idx, i] = fftshift(ifft2(fftshift(proppedWave))) * (self.hololen * self.dk * self.hololen * self.dk)/(2 * np.pi)

            # Energy conservation
            spectral_maskNumber = np.sum(self.spectral_mask_uncentered**2)
            print(spectral_maskNumber)

            reconField = np.fft.ifftshift(ifft2(np.fft.ifftshift(proppedWave))) * (self.hololen*self.dk * self.hololen*self.dk)/(2*np.pi)

            E_image = np.sum(self._apodized_hologram * np.conj(self._apodized_hologram)) * self._pix_width_x*self._pix_width_y
            E_fft = np.sum(ang_spec * np.conj(ang_spec)) * self.dk**2
            E_maskedFFT = np.sum(maskedHolo * np.conj(maskedHolo)) * self.dk**2
            E_reconstruction = np.sum(reconField * np.conj(reconField)) * self._pix_width_x*self._pix_width_y
            print('E_image', E_image)
            print('E_fft', E_fft)
            print('E_maskedFFT', E_maskedFFT)
            print('E_reconstruction', E_reconstruction)

        return ReconstructedWave(reconstructed_wave=wave, fourier_mask=self.spectral_mask_uncentered,
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
            self._amplitude_image = np.abs(self.reconstructed_wave*np.conj(self.reconstructed_wave))

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
    im = mpimg.imread('./data/USAF_multi.tif')
    #im = imread('../data/Hologram.tif')

    propagation_distance = 370 #um
    #wvl = [405e-3, 532e-3, 605e-3] #Wavelength um
    wvl = [405e-3] #Wavelength um
    m = 10 #System magnification
    p = 3.45 #um, pixel size (image space)
    dx = p/m

    start_time = time.time()
    holo = Hologram(im, wavelength=wvl,
                    #pix_dx=p, pix_dy=p, system_magnification=m)
                    pix_dx=dx, pix_dy=dx, system_magnification=m)
    print("Elapsed Time: ", time.time()-start_time)

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
#            #plt.imshow( np.log10(np.real((ang_spec*(spectral_mask+0.1))*np.conj(ang_spec*(spectral_mask+0.1)))) , extent=[kx[0],kx[-1],ky[0],ky[-1]], aspect=1, cmap='gray')
#            plt.imshow( np.log10(np.real((ang_spec*(spectral_mask+0.1))*np.conj(ang_spec*(spectral_mask+0.1)))) , aspect=1, cmap='gray')
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



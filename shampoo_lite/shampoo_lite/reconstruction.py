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
#               but much was gutted out henche the 'lite', also
#               many of the algorithms there were not adequate and
#               were redone for our purposes
#
###############################################################################
"""
import time
import numpy as np

from .datatypes import (BOOLDTYPE, FLOATDTYPE, COMPLEXDTYPE, FRAMEDIMENSIONS, NUMFFTTHREADS)
from .util import (circ_prop, crop_image)
from .mask import (Circle, Mask)
from .fftutils import (fftshift, fft2, ifft2, fft3, ifft3, FFT_3)

# Used for spectral peak computation
from scipy.ndimage import gaussian_filter, maximum_filter

#from shampoo_lite.mask import(Circle, Mask)

from numpy.compat import integer_types #used by arrshift

class UpdateError(Exception):
    pass

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
    peaks = np.zeros([wavelength.shape[2],2], dtype=FLOATDTYPE)
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
    def __init__(self,
                 hologram,
                 crop_fraction=None,
                 wavelength=405e-3,
                 rebin_factor=1,
                 pix_dx=3.45,
                 pix_dy=3.45,
                 system_magnification=1.0,
                 fourier_mask=None,
                 apodize=True):
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
        self._rebin_factor = rebin_factor
        self._system_magnification = system_magnification
        #self._random_seed = RANDOM_SEED

        self.hologram = None
        self.hololen = None

        self.fourier_mask = None

        self.propagation_kernel = None
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

        if fourier_mask:
            self.fourier_mask = fourier_mask

        self.set_hologram(hologram, crop_fraction)

        self.set_wavelength(wavelength)
        self.set_pixel_width(pix_dx, pix_dy)
        self._apodized_hologram = self.hologram * self.apodize_mask()
        #self.update_ft_hologram(apodize=apodize)
        #self.update_angular_spectrum(apodize=apodize)

#        if self.wavelength.size != FRAMEDIMENSIONS[2] or self.hololen != FRAMEDIMENSIONS[1]:
#            #print("$$$$$$$$ Adjusted FFT $$$$$$$$$$$")
#            datatypes.FRAMEDIMENSIONS = (self.hololen, self.hololen, self.wavelength.size)
#            #print("Updating FFT shape", FRAMEDIMENSIONS)
#            myFFT3 = FFT_3(FRAMEDIMENSIONS, FLOATDTYPE, COMPLEXDTYPE, threads=NUMFFTTHREADS)
#            fftutils.fft3 = myFFT3.fft3
#            fftutils.ifft3 = myFFT3.ifft3
#            fftutils.fft2 = myFFT3.fft2
#            fftutils.ifft2 = myFFT3.ifft2

    def update_hologram(self, hologram, crop_fraction=None,
                        wavelength=None, rebin_factor=1,
                        pix_dx=None, pix_dy=None,
                        system_magnification=1.0,
                        fourier_mask=None, apodize=True):
        """
        Update the object based on inputs
        This avoids creating a new hologram object
        """
        self._rebin_factor = rebin_factor
        self._system_magnification = system_magnification
        #self._random_seed = RANDOM_SEED

        #self.hologram = None
        #self.hololen = None

        #self.fourier_mask = None

        #self.propagation_kernel = None
        #self.wavelength = None
        #self.wavenumber = None
        #self._pix_width_x = None
        #self._pix_width_y = None
        #self._spectral_peak = None
        #self._chromatic_shift = None
        #self.apodization_window_function = None
        self._ft_hologram = None
        self._angular_spec_hologram = None
        #self._apodize_mask = None
        #self._mgrid = None
        #self._f_mgrid = None
        #self._propagation_array = None
        #self.G = None
        #self.x_peak = None
        #self.y_peak = None

        if fourier_mask:
            self.fourier_mask = fourier_mask

        prev_hololen = self.hololen
        self.set_hologram(hologram, crop_fraction)

        if prev_hololen != self.hololen:
            self._apodize_mask = None
            self._mgrid = None
            self._f_mgrid = None
            self._propagation_array = None
        
        self.set_wavelength(wavelength)
        self.set_pixel_width(pix_dx, pix_dy)
        self._apodized_hologram = self.hologram * self.apodize_mask()
        #self.update_ft_hologram(apodize=apodize)
        #self.update_angular_spectrum(apodize=apodize)

#        if self.wavelength.size != FRAMEDIMENSIONS[2] or self.hololen != FRAMEDIMENSIONS[1]:
#            #print("$$$$$$$$ Adjusted FFT $$$$$$$$$$$")
#            datatypes.FRAMEDIMENSIONS = (self.hololen, self.hololen, self.wavelength.size)
#            #print("Updating FFT shape", FRAMEDIMENSIONS)
#            myFFT3 = FFT_3(FRAMEDIMENSIONS, FLOATDTYPE, COMPLEXDTYPE, threads=NUMFFTTHREADS)
#            fftutils.fft3 = myFFT3.fft3
#            fftutils.ifft3 = myFFT3.ifft3
#            fftutils.fft2 = myFFT3.fft2
#            fftutils.ifft2 = myFFT3.ifft2

    def set_G_factor(self, G_factor_array):
        self.propagation_kernel = G_factor_array

    def update_G_factor(self, propagation_distance):
        #print("fourier_mask type: ", type(self.fourier_mask))
        self.propagation_kernel = self.generate_propagation_kernel(propagation_distance, self.fourier_mask.mask_centered)

    def set_hologram(self, hologram, crop_fraction=None):
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

        square_hologram = _crop_to_square(hologram)
        binned_hologram = _rebin_image(square_hologram, self._rebin_factor)

        # Crop the hologram by factor crop_factor, centered on original center
        if crop_fraction is not None:
            self.hologram = crop_image(binned_hologram, crop_fraction)
        else:
            self.hologram = binned_hologram

        # Update parameters dependent on hololen

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
            self._ft_hologram = fftshift(fft2(self._apodized_hologram))
        else:
            self._ft_hologram = fftshift(fft2(self.hologram))

        return self._ft_hologram

    def update_angular_spectrum(self, apodize=False):
        if apodize:
            self._angular_spec_hologram = fftshift(fft2(fftshift(self._apodized_hologram)) * self._pix_width_x * self._pix_width_y / (2 * np.pi))
        else:
            self._angular_spec_hologram = fftshift(fft2(fftshift(self.hologram)) * self._pix_width_x * self._pix_width_y / (2 * np.pi))
    
        return self._angular_spec_hologram

    @property
    def ft_hologram(self, apodize=False):
        """
        Return the FT of hologram

        If internal ft_hologram exists, then return that, else
        compute recompute fourier transform and update.
        """
        if self._ft_hologram is None:

            self.update_ft_hologram(apodize=apodize)

        #print('FT_HOLOGRM type: ', self._ft_hologram.dtype)
        return self._ft_hologram


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
            effective_pixel_size = pix_dx / self._system_magnification # object space
            self._pix_width_x = effective_pixel_size * self._rebin_factor
        if pix_dy:
            effective_pixel_size = pix_dy / self._system_magnification # object space
            self._pix_width_y =  effective_pixel_size * self._rebin_factor

        self.dk = 2 * np.pi / (self.hololen * self._pix_width_x)

    def update_propagation_array(self):
        """
        """
        k0 = reshape_to_3d(self.wavenumber, FLOATDTYPE)
        self._propagation_array = np.zeros((self.hololen, self.hololen, self.wavenumber.size), dtype=FLOATDTYPE)

        for i in range(k0.size):
            k = k0[0, 0, i]
            np.sqrt(k**2 - (self.f_mgrid[0]**2 + self.f_mgrid[1]**2) * circ_prop(self.f_mgrid[0], self.f_mgrid[1], k), out=self._propagation_array[:, :, i], dtype=FLOATDTYPE)

        return self._propagation_array

    @property
    def propagation_array(self):
        if self._propagation_array is None:
            self.update_propagation_array()
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
            kx = np.arange(-1 * self.hololen/2, self.hololen/2) * self.dk
            ky = np.arange(-1 * self.hololen/2, self.hololen/2) * self.dk
            self._f_mgrid = np.meshgrid(kx, ky) # meshgrid of pixels, useful for indexing

        return self._f_mgrid

    def apodize_mask(self):
        if self._apodize_mask is None:
            self._apodize_mask = np.cos((self.mgrid[0]-self.hololen/2)/self.hololen*np.pi)**0.25 * np.cos((self.mgrid[1]-self.hololen/2)/self.hololen*np.pi)**0.25

        return self._apodize_mask

    @property
    def angular_spectrum(self, apodize=True):
        """
        """
        if self._angular_spec_hologram is None:
            if apodize:
                self._angular_spec_hologram = fftshift(fft2(fftshift(self._apodized_hologram)) * self._pix_width_x * self._pix_width_y / (2 * np.pi))
            else:
                self._angular_spec_hologram = fftshift(fft2(fftshift(self.hologram)) * self._pix_width_x * self._pix_width_y / (2 * np.pi))
    
        #print('ANGULAR_SPECTRUM type: ', self._angular_spec_hologram.dtype)
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


    #@profile
    def generate_propagation_kernel(self, propagation_distance, spectral_mask_centered):
        """
        Compute and return propagation kernel

        Parameters
        ----------
        propagation_distance : float
            Propagation disance in units of um
        spectral_mask_centered : N x N x wavelength.size np.array
            Spectral mask(s) where the mask is in the center of the image

        Return : N x N x wavelength.size np.array
           Propagation kernel array
        """
        print("GENERATE PROPAGATION KERNEL")
        propKernel = np.zeros((self.hololen, self.hololen, self.wavelength.size), dtype=COMPLEXDTYPE)

        for i, _ in enumerate(self.wavelength):
            propKernel[spectral_mask_centered[:,:,i], i] = np.exp(1j*propagation_distance*self.propagation_array[spectral_mask_centered[:,:,i], i])

        return propKernel

    def generate_spectral_mask(self, compute_spectral_peak=False, center_x=None, center_y=None, radius=250):
        """
        """

        if not compute_spectral_peak:
            if center_x is None or center_y is None:
                raise ValueError("Center_x, center_y and radius must be a scalar or array when compute_spectal_peak is FALSE")

        circle_list = []

        if compute_spectral_peak:

            radius = np.atleast_1d(radius)
            # Find location of all spectral peaks per wavelength. These are the center of the fourier mask
            self._spectral_peak = None
            spectral_peak_loc= self.spectral_peak
            #print(spectral_peak_loc)

            for i in range(self.wavelength.size):
                circle_list.append(Circle(spectral_peak_loc[1][i], spectral_peak_loc[0][i], radius[0]))

        else:
            center_x = np.atleast_1d(center_x)
            center_y = np.atleast_1d(center_y)
            radius = np.atleast_1d(radius)

            if center_x.size != self.wavelength.size or center_y.size != self.wavelength.size or radius.size != self.wavelength.size:
                raise ValueError("Center_x, center_y, and radius must be list or array of same length as wavelength array")

            for i in range(self.wavelength.size):

                circle_list.append(Circle(center_x[i], center_y[i], radius[i]))

        self.fourier_mask = Mask(self.hololen, circle_list, self.dk)

        return self.fourier_mask

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

    ###################################################################3
    ###              Reconstruction
    ###################################################################3
    #@profile
    def reconstruct(self, propagation_distance, compute_spectral_peak=False,
                    compute_digital_phase_mask=False, digital_phase_mask=None, fourier_mask=None,
                    chromatic_shift=None, G_factor=None):
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


        # Compute the angular spectrum
        self.angular_spectrum

        # Compute the fourier mask or used the input fourier mask
        if compute_spectral_peak or self.fourier_mask is None and fourier_mask is None:

            print("GENERATE SPECTRAL MASK")
            self.generate_spectral_mask(compute_spectral_peak=True)

        elif fourier_mask:

            if not isinstance(fourier_mask, Mask):
                raise ValueError("Fourier mask must be of type Mask")

            self.fourier_mask = fourier_mask

            # If fourier mask not expected shape, then generate spectral mask
            if self.fourier_mask.mask.shape[0] != self.hololen or self.fourier_mask.mask.shape[1] != self.hololen or self.fourier_mask.mask.shape[2] != self.wavelength.size:
                print("GENERATE SPECTRAL MASK")
                self.generate_spectral_mask(compute_spectral_peak=True)

        if self.propagation_kernel is None and G_factor is None:
            self.update_G_factor(propagation_distance[0, 0, 0])
        else:
            if not isinstance(G_factor, np.ndarray) or G_factor.shape[0] != self.hololen or G_factor.shape[0] != G_factor.shape[1] or G_factor.shape[2] != self.wavelength.size:
                raise ValueError("G_factor propgation distance must be shape (%d, %d, %d)"%(self.hololen, self.hololen, self.wavelength.size))
            self.propagation_kernel = G_factor

        # Initialize the reconstructed wave array
        wave = np.zeros((self.hololen, self.hololen, propagation_distance.size, self.wavelength.size), dtype=self.angular_spectrum.dtype)

        for i in range(self.wavelength.size):
            for dist_idx in range(propagation_distance.size):

                #dist_idx = 0 # because we going to process a single propagation distance only

                # proppsedWave = maskedHolo * self.propagation_kernel[:, :, dist_idx]
                proppedWave = np.roll(self.angular_spectrum * self.fourier_mask.mask_uncentered[:, :, i],
                                     (int(self.hololen/2 - self.fourier_mask.mask_coordinates[i][1]), int(self.hololen/2 - self.fourier_mask.mask_coordinates[i][0])),
                                     axis=(0, 1)) * self.propagation_kernel[:, :, dist_idx]
    
    
                #proppedWave = self.propagation_kernel[:, :, dist_idx] * maskedHolo
                wave[:, :, dist_idx, i] = fftshift(ifft2(fftshift(proppedWave))) * (self.hololen * self.dk * self.hololen * self.dk)/(2 * np.pi)
    
                ### Energy conservation
                #spectral_maskNumber = self.fourier_mask.mask_number;
                #print(spectral_maskNumber)
                #reconField = np.fft.ifftshift(ifft2(np.fft.ifftshift(proppedWave))) * (self.hololen*self.dk * self.hololen*self.dk)/(2*np.pi)
                #E_image = np.sum(self._apodized_hologram * np.conj(self._apodized_hologram)) * self._pix_width_x*self._pix_width_y
                #E_fft = np.sum(ang_spec * np.conj(ang_spec)) * self.dk**2
                #E_maskedFFT = np.sum(maskedHolo * np.conj(maskedHolo)) * self.dk**2
                #E_reconstruction = np.sum(reconField * np.conj(reconField)) * self._pix_width_x*self._pix_width_y
                #print('E_image', E_image)
                #print('E_fft', E_fft)
                #print('E_maskedFFT', E_maskedFFT)
                #print('E_reconstruction', E_reconstruction)

        return ReconstructedWave(reconstructed_wave=wave)

class ReconstructedWave():
    """
    Container for reconstructed waves and their intensity and phase
    arrays.
    """
    #def __init__(self, reconstructed_wave, fourier_mask, wavelength, depths):
    def __init__(self, reconstructed_wave):
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
        #self.depths = np.atleast_1d(depths)
        self._amplitude_image = None
        self._intensity_image = None
        self._phase_image = None
        #self.fourier_mask = fourier_mask #np.asarray(fourier_mask, dtype=BOOLDTYPE)
        #self.wavelength = np.atleast_1d(wavelength)
        #self._random_seed = RANDOM_SEED

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
            #self._amplitude_image = np.abs(self.reconstructed_wave)

            print("AMPLITUDE Type: ", self._amplitude_image.dtype)
            print(time.time())
        return self._amplitude_image

    @property
    def phase(self):
        """
        `~numpy.ndarray` of the reconstructed, unwrapped phase.

        Returns the unwrapped phase using `~skimage.restoration.unwrap_phase`.
        """
        if self._phase_image is None:
            self._phase_image = np.angle(self.reconstructed_wave)
            print("PHASE Type: ", self._phase_image.dtype)
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

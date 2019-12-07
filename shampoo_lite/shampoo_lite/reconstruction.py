import numpy as np

from datatypes import *

from fftutils import (fftshift, fft2)

###########################################################
###              Constants
###########################################################
RANDOM_SEED = 42

###########################################################
###              Classes
###########################################################
class Hologram(object):
    """
    Container for holograms and methods to reconstruct them.
    """
    def __init__(self, hologram, crop_fraction=None, wavelength=405e-3,
                  rebin_factor=1, dx=3.45, dy=3.45, system_magnification=1.0, mask=None):

        wavelength = np.atleast_1d(wavelength).reshape((1,1,-1)).astype(FLOATDTYPE)

        self.crop_fraction = crop_fraction
        self.rebin_factor = rebin_factor

        # Ensure hologram is a 2D array
        hologram = np.asarray(hologram, dtype = FLOATDTYPE)
        if hologram.ndim != 2:
            raise ValueError('hologram dimensions ({}) are invalid. Holograms should be 2D image'.format(hologram.shape))

        # Rebin the hologram
        square_hologram = _crop_to_square(hologram)
        binned_hologram = _rebin_image(square_hologram, self.rebin_factor)

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
        self.dx = dx/system_magnification*rebin_factor
        self.dy = dy/system_magnification*rebin_factor
        self.system_magnification = system_magnification
        self.random_seed = RANDOM_SEED
        self.apodization_window_function = None
        self._ft_hologram = None
        self._apodize_mask = None
        self._angular_spec_hologram = None
        self._mgrid = None
        self.G = None
        self.mask = mask
        self.x_peak = None
        self.y_peak = None

    @property
    def mgrid(self):
        if self._mgrid is None:
            self._mgrid = np.meshgrid(np.arange(0,self.n),np.arange(0,self.n)) # meshgrid of pixels, useful for indexing

        return self._mgrid

    @property
    def apodize_mask(self):
        if self._apodize_mask is None:
            self._apodize_mask = np.cos((self.mgrid[0]-self.n/2)/self.n*np.pi)**0.25 * np.cos((self.mgrid[1]-self.n/2)/self.n*np.pi)**0.25

        return self._apodize_mask

    @property
    def angular_spectrum(self, apodize=True):
        if self._angular_spec_hologram is None:
            if apodize:
                self._angular_spec_hologram = fftshift(fft2(fftshift(self.hologram*self.apodize_mask)) * self.dx*self.dy/(2*np.pi))
                pass
            else:
                self._angular_spec_hologram = fftshift(fft2(fftshift(self.hologram)) * self.dx*self.dy/(2*np.pi))

        return self._angular_spec_hologram

###################################################################3
###              Support Functions
###################################################################3
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

def _rebin_image(a, binning_factor):
    # Courtesy of J.F. Sebastian: http://stackoverflow.com/a/8090605
    if binning_factor == 1:
        return a

    new_shape = (a.shape[0]/binning_factor, a.shape[1]/binning_factor)
    sh = (new_shape[0], a.shape[0]//new_shape[0], new_shape[1],
          a.shape[1]//new_shape[1])
    return a.reshape(map(int, sh)).mean(-1).mean(1)


if __name__ == "__main__":
    import matplotlib.pyplot as plt
    from skimage.io import imread

    showFigs = True

    im = imread('../data/USAF_multi.tif')

    wvl = [405e-3, 532e-3, 605e-3] #Wavelength um
    m = 10 #System magnification
    p = 3.45 #um, pixel size (image space)
    dx = p/m;

    holo = Hologram(im, wavelength=405e-3,
                  dx=p, dy=p, system_magnification=m)


    apoMask = np.cos((holo.mgrid[0]-holo.n/2)/holo.n*np.pi)**0.25 * np.cos((holo.mgrid[1]-holo.n/2)/holo.n*np.pi)**0.25
    ang_spec = holo.angular_spectrum

if showFigs:
    x = np.arange(-holo.n/2,holo.n/2) * holo.dx # Object space x and y vectors
    y = np.arange(-holo.n/2,holo.n/2) * holo.dy
    X, Y = np.meshgrid(x, y) # Object space x and y matrices

    dk = 2*np.pi/(holo.n*holo.dx)
    kx = np.arange(-holo.n/2,holo.n/2) * dk
    ky = np.arange(-holo.n/2,holo.n/2) * dk
    Kx, Ky = np.meshgrid(kx, ky)

    # Plot the results
    plt.figure(1)
    plt.imshow(holo.hologram, extent=[x[0], x[-1], y[0], y[-1]], aspect=1, cmap='gray')
    plt.xlabel('Object Space, um')
    plt.title('Raw Hologram - US Air Force Resolution Target')
    #plt.show()

    plt.figure(2)
    plt.imshow( np.log(np.abs(ang_spec)) , extent=[kx[0],kx[-1],ky[0],ky[-1]], aspect=1, cmap='gray')
    plt.xlabel('Frequency Space, um^-1')
    plt.title('Angular Spectrum - Showing Masked Region')
    plt.show()

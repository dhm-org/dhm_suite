
import numpy as np
from .datatypes import (BOOLDTYPE)
from .util import (circ_prop)

class Circle(object):

    def __init__(self, centerx, centery, radius):
        self.centerx = centerx
        self.centery = centery
        self.radius = radius
        self._params = None
        self.get_params

    @property
    def get_params(self):
        if self._params is None:
            self._params = (self.centerx, self.centery, self.radius)
        return self._params

class Mask(object):
    def __init__(self, N, circle_list, dk):

        self.kx = np.arange(-N/2, N/2) * dk
        self.ky = np.arange(-N/2, N/2) * dk
        self.f_mgrid = np.meshgrid(self.kx, self.ky)

        print(self.kx.shape, self.ky.shape)

        self.N = N
        self.circle_list = circle_list
        self.dk = dk

        self._mask_centered = np.zeros((self.N, self.N, len(self.circle_list)), dtype=BOOLDTYPE) 
        self._mask_uncentered = np.zeros((self.N, self.N, len(self.circle_list)), dtype=BOOLDTYPE) 
        self._mask_coordinates = []

        for _ in range(len(self.circle_list)):

            centerx, centery, radius = self.circle_list[_].get_params
            self._mask_coordinates.append(self.circle_list[_].get_params)
            self._mask_uncentered[:, :, _], \
            self._mask_centered[:, :, _] = self.spectral_mask(centerx, centery, radius)

        self._mask_number = np.sum(self._mask_uncentered ** 2)

    @property
    def mask(self):
        return self._mask_uncentered 

    @property
    def mask_uncentered(self):
        return self._mask_uncentered 

    @property
    def mask_centered(self):
        return self._mask_centered 

    @property
    def mask_coordinates(self):
        return self._mask_coordinates

    @property
    def mask_number(self):
        return self._mask_number
        
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
        centerX = self.kx[center_x_pix] # um^-1 frequency coordinate
        centerY = self.ky[center_y_pix] # um^-1
        radius = radius_pix * self.dk # um^-1
        spectral_mask_uncentered = (circ_prop(self.f_mgrid[0]-centerX, self.f_mgrid[1]-centerY, radius) > 0.5)
        spectral_mask_centered = (circ_prop(self.f_mgrid[0], self.f_mgrid[1], radius) > 0.5)

        return (spectral_mask_uncentered, spectral_mask_centered,)

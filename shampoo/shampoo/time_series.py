# -*- coding: utf-8 -*-
"""
This module implements storage of holographic time-series
via an HDF5 file.
"""

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from collections import Iterable

import h5py
import numpy as np

from .reconstruction import Hologram, ReconstructedWave

class TimeSeries(h5py.File):
    """
    Holographic time-series as an HDF5 archive.

    Attributes
    ----------
    time_points : tuple of floats
        Time-points in seconds
    wavelengths : tuple of floats
        Wavelengths in nm.
    """
    _default_ckwargs = dict() #{'chunks': True, 
                       # 'compression':'lzf', 
                       # 'shuffle': True}
    
    @property
    def time_points(self):
        return tuple(self.attrs.get('time_points', default = tuple()))
    
    @property
    def wavelengths(self):
        return tuple(self.attrs.get('wavelengths', default = tuple()))
    
    @property
    def depths(self):
        return tuple(self.attrs.get('depths', default = tuple()))

    @property
    def hologram_group(self):
        return self.require_group('holograms')
    
    @property
    def reconstructed_group(self):
        return self.require_group('reconstructed')
    
    @property
    def fourier_mask_group(self):
        return self.require_group('/reconstructed/fourier_masks')

    def add_hologram(self, hologram, time_point = 0):
        """
        Add a hologram to the time-series.

        Parameters
        ----------
        hologram : Hologram

        time_point : float, optional

        Raises
        ------
        ValueError
            If the hologram is not compatible with the current TimeSeries,
            e.g. the wavelengths do not match.
        """
        # TODO: Holograms are stored as UINT8
        #       Is that sensible?
        holo_wavelengths = tuple(hologram.wavelength.reshape((-1)))
        time_point = float(time_point)

        if len(self.time_points) == 0:
            # This is the first hologram. Record the wavelength
            # and this will never change again.
            self.attrs['wavelengths'] = holo_wavelengths
        
        # The entire TimeSeries has the uniform wavelengths
        if not np.allclose(holo_wavelengths, self.wavelengths):
            raise ValueError('Wavelengths of this hologram ({}) do not match the TimeSeries \
                              wavelengths ({})'.format(holo_wavelengths, self.wavelengths))

        # If time-point already exists, we will override the hologram
        # that is already stored there. Otherwise, create a new dataset
        gp = self.hologram_group
        if time_point in self.time_points:
            return gp[str(time_point)].write_direct(hologram.hologram)
        else:
            self.attrs['time_points'] = self.time_points + (time_point, )
            return gp.create_dataset(str(time_point), data = hologram.hologram, 
                                     dtype = np.uint8, **self._default_ckwargs)
    
    def hologram(self, time_point, **kwargs):
        """
        Return Hologram object from archive. Keyword arguments are
        passed to the Hologram constructor.
        
        Parameters
        ----------
        time_point : float
            Time-point in seconds.
        
        Returns
        -------
        out : Hologram

        Raises
        ------
        ValueError
            If the time-point hasn't been recorded in the time-series.
        """
        time_point = float(time_point)
        if time_point not in self.time_points:
            raise ValueError('Time-point {} not in TimeSeries.'.format(time_point))
        
        dset = self.hologram_group[str(time_point)]
        return Hologram(np.array(dset), wavelength = self.wavelengths, **kwargs)

    def reconstruct(self, time_point, propagation_distance, 
                    fourier_mask = None, **kwargs):
        """
        Hologram reconstruction from Hologram.reconstruct(). Keyword arguments
        are also passed to Hologram.reconstruct()
        
        Parameters
        ----------
        time_point : float
            Time-point in seconds.
        propagation_distance : float
            Propagation distance in meters.
        fourier_mask : ndarray or None, optional
            User-specified Fourier mask. Refer to Hologram.reconstruct()
            documentation for details.
        
        Returns
        -------
        out : ReconstructedWave object
            The ReconstructedWave is both stored in the TimeSeries HDF5 file
            and returned to the user. 
        """
        time_point = float(time_point)
        propagation_distance = np.atleast_1d(propagation_distance).tolist()

        # TODO: provide an accumulator array for hologram.reconstruct()
        #       so that depths are written to disk on the fly?
        recon_wave = self.hologram(time_point).reconstruct(propagation_distance, 
                                                           fourier_mask = fourier_mask,
                                                           **kwargs)
        
        # TODO: provide support for re-reconstructing again with different parameters

        self.reconstructed_group.create_dataset(str(time_point), data = recon_wave.reconstructed_wave, 
                                                dtype = np.complex, **self._default_ckwargs)
        self.reconstructed_group[str(time_point)].attrs['depths'] = propagation_distance

        self.fourier_mask_group.create_dataset(str(time_point), data = recon_wave.fourier_mask, 
                                               dtype = np.bool,**self._default_ckwargs)
        
        # Return the same thins as Hologram.reconstruct() so that the TimeSeries can be passed
        # to anything that expect a reconstruct() method.
        return recon_wave
    
    def reconstructed_wave(self, time_point, **kwargs):
        """
        Returns the ReconstructedWave object from archive. 
        Keyword arguments are passed to the ReconstructedWave 
        contructor.

        Parameters
        ----------
        time_point : float
            Time-point in seconds.
        
        Returns
        -------
        out : ReconstructedWave object

        Raises
        ------
        ValueError
            If the reconstruction is unavailable either due to having no
            associated hologram, or reconstruction never having been performed.
        """
        time_point = str(float(time_point))

        gp, fp = self.reconstructed_group, self.fourier_mask_group
        if time_point not in gp:
            raise ValueError('Reconstruction at {} is unavailable or reconstruction \
                              was never performed.'.format(time_point))
        
        wave = gp[time_point]
        mask = fp[time_point]

        return ReconstructedWave(np.array(gp[time_point]), fourier_mask = np.array(fp[time_point]), 
                                 wavelength = self.wavelengths, depths = gp[time_point].attrs['depths'])
        
    def batch_reconstruct(self, propagation_distance, fourier_mask = None,
                          callback = None, **kwargs):
        """ 
        Reconstruct all the holograms stored in the TimeSeries. Keyword 
        arguments are passed to the Hologram.reconstruct() method. 
        
        Parameters
        ----------
        time_point : float
            Time-point in seconds.
        propagation_distance : float
            Propagation distance in meters.
        fourier_mask : ndarray or None, optional
            User-specified Fourier mask. Refer to Hologram.reconstruct()
            documentation for details.
        callback : callable, optional
            Callable that takes an int between 0 and 99. The callback will be
            called after each reconstruction with the proportion of completed
            reconstruction.
        """
        if callback is None:
            callback = lambda i: None 
            
        total = len(self.time_points)
        
        for index, time_point in enumerate(self.time_points):
            self.reconstruct(time_point = time_point, 
                             propagation_distance = propagation_distance,
                             fourier_mask = fourier_mask, **kwargs)
            callback(int(100*index / total))
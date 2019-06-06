# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os.path
import tempfile

import numpy as np

from ..reconstruction import RANDOM_SEED, Hologram, ReconstructedWave
from ..time_series import TimeSeries

np.random.seed(RANDOM_SEED)

def _example_hologram(dim = 512):
    """ Generate example Hologram object """
    return 200*np.ones((dim, dim), dtype = np.uint8) + np.random.randint(low = 0, high = 255, 
                                                                         size = (dim, dim), dtype = np.uint8)

def test_time_series_metadata_defaults():
    name = os.path.join(tempfile.gettempdir(), 'test_time_series.hdf5')
    with TimeSeries(name = name, mode = 'w') as time_series:

        # Check default values when newly-created object
        assert time_series.time_points == tuple()
        assert time_series.wavelengths == tuple()

def test_time_series_storing_hologram_single_wavelength():
    """ Test storage of holograms with a single wavelength """
    name = os.path.join(tempfile.gettempdir(), 'test_time_series.hdf5')
    hologram = Hologram(_example_hologram())
    with TimeSeries(name = name, mode = 'w') as time_series:
        time_series.add_hologram(hologram, time_point = 0)
        time_series.add_hologram(hologram, time_point = 1)

        # Check that internal containmentship tests are working
        assert '0.0' in time_series.hologram_group
        assert '1.0' in time_series.hologram_group

        assert time_series.time_points == (0,1)

        retrieved = time_series.hologram(0)
        assert isinstance(retrieved, Hologram)
        assert retrieved.hologram.ndim == 2
        assert np.allclose(hologram.hologram, retrieved.hologram)
        assert np.allclose(time_series.wavelengths, hologram.wavelength)

def test_time_series_storing_hologram_three_wavelength():
    """ Test storage of holograms with three wavelengths """
    name = os.path.join(tempfile.gettempdir(), 'test_time_series.hdf5')
    hologram = Hologram(np.zeros(shape = (512, 512), dtype = np.uint8), 
                        wavelength = [1,2,3])
    with TimeSeries(name = name, mode = 'w') as time_series:
        time_series.add_hologram(hologram, time_point = 0)
        time_series.add_hologram(hologram, time_point = 1)
        
        assert np.allclose(time_series.time_points, (0,1))
        assert np.allclose(time_series.wavelengths, (1,2,3))

        assert np.allclose(hologram.hologram, time_series.hologram(0).hologram)
        assert np.allclose(hologram.hologram, time_series.hologram(1).hologram)

        assert time_series.hologram(0).hologram.ndim == 2
        assert time_series.hologram(1).hologram.ndim == 2

def test_time_series_reconstruct_single_wavelength():
    name = os.path.join(tempfile.gettempdir(), 'test_time_series.hdf5')
    hologram = Hologram(_example_hologram())
    with TimeSeries(name = name, mode = 'w') as time_series:
        time_series.add_hologram(hologram, time_point = 0)
        ts_reconw = time_series.reconstruct(time_point = 0,
                                            propagation_distance = 1) 
        assert isinstance(ts_reconw, ReconstructedWave) 
        
        # Retrieve reconstructed wave from archive
        archived_reconw = time_series.reconstructed_wave(time_point = 0)
        
        assert isinstance(archived_reconw, ReconstructedWave)

        assert np.allclose(ts_reconw.reconstructed_wave, 
                           archived_reconw.reconstructed_wave)

def test_time_series_reconstruct_three_wavelength_single_depth():
    name = os.path.join(tempfile.gettempdir(), 'test_time_series.hdf5')
    hologram = Hologram(_example_hologram(), wavelength = [100e-9, 200e-9, 300e-9])

    with TimeSeries(name = name, mode = 'w') as time_series:
        time_series.add_hologram(hologram, time_point = 0)
        ts_reconw = time_series.reconstruct(time_point = 0,
                                            propagation_distance = 1) 
        assert isinstance(ts_reconw, ReconstructedWave) 
        
        # Retrieve reconstructed wave from archive
        archived_reconw = time_series.reconstructed_wave(time_point = 0)
        
        assert isinstance(archived_reconw, ReconstructedWave)

        assert np.allclose(ts_reconw.reconstructed_wave, 
                           archived_reconw.reconstructed_wave)

def test_time_series_reconstruct_three_wavelength_multi_depth():
    name = os.path.join(tempfile.gettempdir(), 'test_time_series.hdf5')
    hologram = Hologram(_example_hologram(), wavelength = [100e-9, 200e-9, 300e-9])

    with TimeSeries(name = name, mode = 'w') as time_series:
        time_series.add_hologram(hologram, time_point = 0)
        ts_reconw = time_series.reconstruct(time_point = 0,
                                            propagation_distance = [0.1, 0.2, 0.3]) 
        assert isinstance(ts_reconw, ReconstructedWave)
        assert ts_reconw.reconstructed_wave.shape == hologram.hologram.shape + (3, 3)

def test_time_series_batch_reconstruct_single_wavelength():
    name = os.path.join(tempfile.gettempdir(), 'test_time_series.hdf5')

    with TimeSeries(name = name, mode = 'w') as time_series:
        for time_point in range(3):
            h = Hologram(_example_hologram())
            time_series.add_hologram(h, time_point = time_point)
        
        time_series.batch_reconstruct(propagation_distance = 1)

def test_time_series_batch_reconstruct_three_wavelengths():
    name = os.path.join(tempfile.gettempdir(), 'test_time_series.hdf5')

    with TimeSeries(name = name, mode = 'w') as time_series:
        for time_point in range(3):
            h = Hologram(_example_hologram(), wavelength = [400e-9, 500e-9, 600e-9])
            time_series.add_hologram(h, time_point = time_point)
        
        time_series.batch_reconstruct(propagation_distance = 1)
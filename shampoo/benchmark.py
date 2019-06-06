"""
Script for determining the bottlenecks of Hologram.reconstruct()
"""
import numpy as np
from shampoo.tests.test_hologram import _example_hologram
from shampoo import Hologram

if __name__ == '__main__':
    # Single wavelength
    holo = Hologram(_example_hologram(dim = 2048), wavelength = 800)
    for p in np.linspace(0.01, 0.04, num = 30):
        holo.reconstruct(p)
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from ..reconstruction import (Hologram, rebin_image, _find_peak_centroid,
                              RANDOM_SEED, _crop_image, CropEfficiencyWarning)

import numpy as np
np.random.seed(RANDOM_SEED)

import pytest

def _example_hologram(dim=256):
    """
    Generate example hologram.

    Parameters
    ----------
    dim : int
        Dimensions of image. Default is 2048.
    """
    return 1000*np.ones((dim, dim)) + np.random.randn(dim, dim)

def test_non2d_hologram():
    """ Test that non-2D holograms raise a ValueError on instantiation """
    with pytest.raises(ValueError) as e_info:
        holo = Hologram(np.empty((128, 128, 3)))

def test_load_hologram():
    holo = Hologram(_example_hologram())
    assert holo is not None

def test_rebin_image():
    dim = 2048
    full_res = _example_hologram(dim=dim)
    assert (dim//2, dim//2) == rebin_image(full_res, 2).shape

def test_nondefault_fourier_mask():
    im = _example_hologram()
    holo = Hologram(im)
    mask = np.random.randint(0, 2, size = im.shape).astype(np.bool)
    w = holo.reconstruct(0.5, fourier_mask = mask)

    assert np.allclose(np.squeeze(w.fourier_mask), np.squeeze(mask))

def test_reconstruction_multiwavelength():
    wl = [450e-9, 550e-9, 650e-9]
    im = _example_hologram()
    holo = Hologram(im, wavelength = wl)

    w = holo.reconstruct(0.2)
    assert np.allclose(wl, holo.wavelength)
    assert len(wl) == w.reconstructed_wave.shape[3]

    # in some rare occations, it has appeared that the
    # reconstructed waves were all NaNs.
    assert np.all(np.isfinite(w.reconstructed_wave))

def test_reconstruction_single_wavelength_multiple_depths():
    im = _example_hologram()
    holo = Hologram(im)

    w = holo.reconstruct([0.2, 0.3, 0.4])
    assert w.reconstructed_wave.shape == ( holo.hologram.shape + (3, 1))   # (X, Y, Z, wavelengths)

def test_reconstruction_multiple_wavelengths_multiple_depths():
    im = _example_hologram()
    wl = [450e-9, 550e-9, 650e-9]
    holo = Hologram(im, wavelength = wl)

    w = holo.reconstruct([0.2, 0.3])
    assert w.reconstructed_wave.shape == ( holo.hologram.shape + (2, len(wl)))   # (X, Y, Z, wavelengths)

def _gaussian2d(amplitude, width, centroid, dim):
    x, y = np.mgrid[0:dim, 0:dim]
    x_centroid, y_centroid = centroid
    return amplitude*np.exp(-0.5 * ((x - x_centroid)**2/width**2 +
                                    (y - y_centroid)**2/width**2))


def test_centroid():
    centroid = np.array([(308, 308), (512,512), (716,716)])
    amp = np.array([10, 20, 10])
    test_image = np.zeros([1024,1024])
    for c in range(len(centroid)):
        test_image = test_image + _gaussian2d(amplitude=amp[c], width=5, centroid=centroid[c], dim=1024)
    assert np.all(np.squeeze(_find_peak_centroid(image=test_image)) == centroid.swapaxes(0,1)[:,2])
    assert np.any(test_image[centroid] == np.max(test_image))

def test_centroid_multichannel():
    """ Test _find_peak_centroid for inputs with multiple channels (wavelengths) """
    wl = [450e-9, 550e-9, 650e-9]
    centroid = np.array([(308, 308), (512,512), (624,224), (824,424), (716,716), (400,800), (200,600)])
    amp = np.array([10, 8, 6, 20, 6, 8, 10])
    test_image = np.zeros([1024,1024])
    for c in range(len(centroid)):
        test_image = test_image + _gaussian2d(amplitude=amp[c], width=5, centroid=centroid[c], dim=1024)

    assert np.all(np.squeeze(_find_peak_centroid(image=test_image,wavelength=wl)) == centroid[4:])
    assert np.any(test_image[centroid] == np.max(test_image))

def test_crop_image():
    # Even number rows/cols
    image1 = np.arange(1024).reshape((32, 32))
    new_shape1 = (image1.shape[0]//2, image1.shape[1]//2)
    cropped_image1 = _crop_image(image1, 0.5)
    assert new_shape1 == cropped_image1.shape

    # Odd number rows/cols
    image2 = np.arange(121).reshape((11, 11))
    new_shape2 = (image2.shape[0]//2, image2.shape[1]//2)
    cropped_image2 = _crop_image(image2, 0.5)
    assert new_shape2 == cropped_image2.shape

def test_phase_unwrapping_single_wavelength():
    im = _example_hologram()
    holo = Hologram(im)

    w = holo.reconstruct([0.2, 0.3, 0.4])
    assert w.reconstructed_wave.shape == w.phase.shape + (1,)

def test_phase_unwrapping_multi_wavelength():
    im = _example_hologram()
    wl = [450e-9, 550e-9, 650e-9]
    holo = Hologram(im, wavelength = wl)

    w = holo.reconstruct([0.2, 0.3])
    assert w.reconstructed_wave.shape == w.phase.shape

def test_multiple_reconstructions():
    """
    At commit cc730bd and earlier, the Hologram.apodize function modified
    the Hologram.hologram array every time Hologram.reconstruct was called.
    This tests that that should not happen anymore.
    """

    propagation_distances = [0.5, 0.8]
    holo = Hologram(_example_hologram())
    h_raw = holo.hologram.copy()
    holograms = []

    for d in propagation_distances:
        w = holo.reconstruct(d)
        holograms.append(holo.hologram)

    # check hologram doesn't get modified in place first time
    assert np.all(h_raw == holograms[0])

    # check hologram doesn't get modified again
    assert np.all(holograms[0] == holograms[1])


def test_nonsquare_hologram():
    sq_holo = _example_hologram()
    nonsq_holo = sq_holo[:-10, :]

    holo = Hologram(nonsq_holo)
    w = holo.reconstruct(0.5)

    phase_shape = w.phase.shape

    assert phase_shape[0] == min(nonsq_holo.shape)
    assert phase_shape[1] == min(nonsq_holo.shape)

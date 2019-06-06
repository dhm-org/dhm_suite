"""
This module is a wrapper around ``pyfftw``'s API for fast Fourier transforms.
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import pyfftw
import numpy as np
from numpy.compat import integer_types

pyfftw.interfaces.cache.enable()

__all__ = ['FFT', 'FFT_3', 'fftshift']


class FFT_3(object):
    """
    Convenience wrapper around ``pyfftw.builders.fft2``.
    """
    def __init__(self, shape, float_precision, complex_precision, threads=2, planner_effort='FFTW_ESTIMATE'):
        """
        Parameters
        ----------
        shape : tuple
            Shape of the arrays which you will take the Fourier transforms of.
        float_precision : `~numpy.dtype`
        complex_precision : `~numpy.dtype`
        threads : int, optional
            This FFT implementation uses multithreading, with
            two threads by default.
        """
        # Allocate byte-aligned
        self.shape = shape
        self.buffer_float = pyfftw.empty_aligned(shape,
                                                 dtype=float_precision.__name__)
        self.buffer_complex = pyfftw.empty_aligned(shape,
                                                   dtype=complex_precision.__name__)
        self._fft3 = pyfftw.builders.fftn(self.buffer_float, axes=(0,1), threads=threads, planner_effort=planner_effort)
        self._ifft3 = pyfftw.builders.ifftn(self.buffer_complex, axes=(0,1),
                                            threads=threads, planner_effort=planner_effort)

    def fft3(self, array):
        """
       N-D Fourier transform.

        Parameters
        ----------
        array : `~numpy.ndarray` (real)
            Input array

        Returns
        -------
        ft_array : `~numpy.ndarray` (complex)
            Fourier transform of the input array
        """
        self._fft3.input_array[:] = array
        return self._fft3()

    def fft2(self, array):
        """
       2-D Fourier transform.

        Parameters
        ----------
        array : `~numpy.ndarray` (real)
            Input array

        Returns
        -------
        ft_array : `~numpy.ndarray` (complex)
            Fourier transform of the input array
        """
        self._fft3.input_array[:,:,0] = array
        ret = self._fft3()[:,:,0]
        return ret

    def ifft3(self, array):
        """
        Inverse 3D Fourier transform.

        Parameters
        ----------
        array : `~numpy.ndarray`
            Input array

        Returns
        -------
        ift_array : `~numpy.ndarray`
            Inverse Fourier transform of input array
        """
        self._ifft3.input_array[:] = array
        #return self._ifft3()[:,:,0:array.shape[2]]
        return self._ifft3()

    def ifft2(self, array):
        """
        Inverse 3D Fourier transform.

        Parameters
        ----------
        array : `~numpy.ndarray`
            Input array

        Returns
        -------
        ift_array : `~numpy.ndarray`
            Inverse Fourier transform of input array
        """
        self._ifft3.input_array[:,:,0] = array
        return self._ifft3()[:,:,0]


class FFT(object):
    """
    Convenience wrapper around ``pyfftw.builders.fft2``.
    """
    def __init__(self, shape, float_precision, complex_precision, threads=2):
        """
        Parameters
        ----------
        shape : tuple
            Shape of the arrays which you will take the Fourier transforms of.
        float_precision : `~numpy.dtype`
        complex_precision : `~numpy.dtype`
        threads : int, optional
            This FFT implementation uses multithreading, with
            two threads by default.
        """
        # Allocate byte-aligned
        self.buffer_float = pyfftw.empty_aligned(shape,
                                                 dtype=float_precision.__name__)
        self.buffer_complex = pyfftw.empty_aligned(shape,
                                                   dtype=complex_precision.__name__)
        self._fft2 = pyfftw.builders.fft2(self.buffer_float, threads=threads)
        self._ifft2 = pyfftw.builders.ifft2(self.buffer_complex,
                                            threads=threads)

    def fft2(self, array):
        """
        2D Fourier transform.

        Parameters
        ----------
        array : `~numpy.ndarray` (real)
            Input array

        Returns
        -------
        ft_array : `~numpy.ndarray` (complex)
            Fourier transform of the input array
        """
        self._fft2.input_array[:] = array
        return self._fft2()

    def ifft2(self, array):
        """
        Inverse 2D Fourier transform.

        Parameters
        ----------
        array : `~numpy.ndarray`
            Input array

        Returns
        -------
        ift_array : `~numpy.ndarray`
            Inverse Fourier transform of input array
        """
        self._ifft2.input_array[:] = array
        return self._ifft2()


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

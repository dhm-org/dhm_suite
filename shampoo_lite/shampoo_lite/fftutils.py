
__all__ = ['fft2', 'fftshift']

try:
    import multiprocessing
    from pyfftw_utils import (FFT_3, fftshift)
    from datatypes import (FLOATDTYPE, COMPLEXDTYPE)

    FRAMEDIMENSIONS = (2048, 2048, 1)
    NUMFFTTHREADS = multiprocessing.cpu_count()/2
    myFFT3 = None
    fft3   = None
    ifft3  = None
    fft2   = None
    ifft2  = None
    
    myFFT3 = FFT_3(FRAMEDIMENSIONS, FLOATDTYPE, COMPLEXDTYPE, threads=NUMFFTTHREADS)
    fft3   = myFFT3.fft3
    ifft3  = myFFT3.ifft3
    fft2   = myFFT3.fft2
    ifft2  = myFFT3.ifft2

    print('Import FFT utilities from "pyfftw_utils"')
except Exception as e:
    raise e

    import numpy as np
    fft2 = np.fft.fft2
    fftshift = np.fft.fftshift
    print('Import FFT utilities from "numpy"')

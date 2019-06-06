import cython
import numpy as np
cimport numpy as np
cimport cython

cdef extern void compute_G(double *x, double *y, int N, double *wl, int lenwl, double *d, int lenprop, double dx, double dy, double complex *G)
cdef extern void compute_G_f (float *x, float *y, int N, float *wl, int lenwl, float *d, int lenprop, float dx, float dy, float complex *G)
#cdef extern void c_compute_2Dfft (double * _in, double complex *out, int N)
#cdef extern void c_fft_fftshift_2D (double complex *inout, int N)
#cdef extern void c_fft_fftshift_2D_f (float complex *inout, int N)

#@cython.boundscheck(False)
#@cython.wraparound(False)
#def fft2D(np.int N, np.ndarray[np.complex64_t, ndim=2, mode="c"] inout):
#    """
#    """
#    c_fft_fftshift_2D_f(&inout[0,0], N)
    
@cython.boundscheck(False)
@cython.wraparound(False)
def ComputeG_f(np.ndarray[np.float32_t, ndim=2, mode="c"] x, np.ndarray[np.float32_t, ndim=2, mode="c"] y, np.ndarray[np.float32_t, ndim=1, mode="c"] wl, np.ndarray[np.float32_t, ndim=1, mode="c"] propagation_dist, np.int N, np.float32_t dx, np.float32_t dy, np.ndarray[np.complex64_t, ndim=4, mode="c"] G):
    """
    """
    cdef int plen = propagation_dist.shape[0]
    cdef int wlen = wl.shape[0]


    compute_G_f (&x[0,0], &y[0,0], N, &wl[0], wlen, &propagation_dist[0], plen, dx, dy, &G[0,0,0,0])

import numpy as np
import multiprocessing

FLOATDTYPE = np.float64 #np.float32
COMPLEXDTYPE = np.complex64 if FLOATDTYPE == np.float32 else np.complex128

BOOLDTYPE = np.bool

FRAMEDIMENSIONS = (2048, 2048, 1)
NUMFFTTHREADS = multiprocessing.cpu_count()/2



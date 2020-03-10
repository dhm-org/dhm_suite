"""
###############################################################################
#  Copyright 2019, by the California Institute of Technology. ALL RIGHTS RESERVED.
#  United States Government Sponsorship acknowledged. Any commercial use must be
#  negotiated with the Office of Technology Transfer at the
#  California Institute of Technology.
#
#  This software may be subject to U.S. export control laws. By accepting this software,
#  the user agrees to comply with all applicable U.S. export laws and regulations.
#  User has the responsibility to obtain export licenses, or other export authority
#  as may be required before exporting such information to foreign countries or providing
#  access to foreign persons.
#
#  file:	shampoo_lite/datatypes.py
#  author:	S. Felipe Fregoso
#  description:	Defines the datatypes to be used by SHAMPOO-LITE
#
###############################################################################
"""
import numpy as np
import multiprocessing

FLOATDTYPE = np.float32 #np.float32
COMPLEXDTYPE = np.complex64 if FLOATDTYPE == np.float32 else np.complex128

BOOLDTYPE = np.bool

FRAMEDIMENSIONS = (2048, 2048, 1)
NUMFFTTHREADS = multiprocessing.cpu_count()/2



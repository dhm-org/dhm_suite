from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
from Cython.Build import cythonize
import numpy

setup(
    cmdclass = {'build_ext': build_ext},
    ext_modules = [Extension("reconst_util",
                             sources=['reconst_util.pyx', "reconst.c"],
                             extra_compile_args=['-O3', '-fopenmp'],
                             extra_link_args=['-fopenmp'],
                             libraries = ['fftw3f', 'm'], 
                             library_dirs = ['/usr/lib64'],
                             include_dirs=[numpy.get_include()])],
)



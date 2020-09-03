import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="shampoo-lite-SFREGOSO",
    version="0.0.1",
    author="Santos F. Fregoso",
    author_email="sfregoso@jpl.nasa.gov",
    description="Digital holography reconstruction tool",
    url="https://github.com/dhm-org/dhm_suite/tree/master/shampoo_lite",
    classifiers=[
        "Programming Language :: Python :: 3.5",
    ],
    python_requires='>=3.5',
    install_requires=[
        'numpy',
        'pyfftw',
        'scipy',
        'scikit-image',
        'imagecodecs',
    ],
         
)

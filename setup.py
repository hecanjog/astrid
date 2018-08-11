#!/usr/bin/env python
from setuptools import setup

try:
    from Cython.Build import cythonize
    import numpy as np
    ext_modules = cythonize([
        'astrid/io.pyx', 
        'astrid/logger.pyx', 
        'astrid/orc.pyx', 
        'astrid/midi.pyx', 
        'astrid/names.pyx', 
        'astrid/server.pyx', 
        'astrid/q.pyx', 
    ], include_path=[np.get_include()], annotate=True) 

except ImportError:
    from setuptools.extension import Extension
    ext_modules = [
        Extension('astrid.io', 
                 ['astrid/io.c'], 
                 extra_compile_args=['-fopenmp'], 
                 extra_link_args=['-fopenmp']
        ), 
        Extension('astrid.logger', ['astrid/logger.c']), 
        Extension('astrid.orc', ['astrid/orc.c']), 
        Extension('astrid.midi', ['astrid/midi.c']), 
        Extension('astrid.names', ['astrid/names.c']), 
        Extension('astrid.server', ['astrid/server.c']), 
        Extension('astrid.q', 
                 ['astrid/q.c'], 
                 extra_compile_args=['-fopenmp', '-pthreads'], 
                 extra_link_args=['-fopenmp', '-pthreads']
        ), 

    ]


setup(
    name='astrid',
    version='1.0.0-alpha-3',
    description='Interactive computer music with Python',
    author='He Can Jog',
    author_email='erik@hecanjog.com',
    url='https://github.com/hecanjog/astrid',
    scripts = ['bin/astrid'],
    packages=['astrid'],
    ext_modules=ext_modules, 
)

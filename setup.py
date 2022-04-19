#!/usr/bin/env python
# -*- coding: utf-8 -*-

# To make a release type:
#   rm -rf build dist
#   python setup.py sdist --formats=zip

# Then upload to PiPy with
#   twine check dist/*
#   twine upload dist/dcmobjbrowser-1.2.0.zip

from browser import DEBUGGING, PROGRAM_VERSION
from setuptools import setup

assert not DEBUGGING, "DEBUGGING must be False"

setup(name = 'dcmobjbrowser',
    version = PROGRAM_VERSION, 
    description = 'Python DICOM file browser and editor.',
    long_description = open('README.txt').read(),
    long_description_content_type = 'text/x-rst',
    url = 'https://github.com/sperlingn/dcmobjbrowser',
    author = 'Nicholas Sperling', 
    author_email = 'Nicholas.Sperling@utoledo.edu', 
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: X11 Applications :: Qt',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Topic :: Adaptive Technologies',
        'Topic :: Software Development',
        'Topic :: Utilities'],    
    packages = ['dcmobjbrowser'],
    install_requires = ['six', 'qtpy', 'objbrowser'])
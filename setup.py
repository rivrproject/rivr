#!/usr/bin/env python

from distutils.core import setup

VERSION = '0.1.1'

setup(
    name='rivr',
    version=VERSION,
    author='Kyle Fuller',
    author_email='inbox@kylefuller.co.uk',
    url='http://github.com/kylef/rivr/',
    download_url='http://github.com/kylef/rivr/zipball/%s' % VERSION,
    packages=['rivr', 'rivr.middleware', 'rivr.views'],
    license='BSD',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ]
)
#!/usr/bin/env python

from setuptools import setup

from rivr import VERSION

setup(
    name='rivr',
    version=VERSION,
    author='Kyle Fuller',
    author_email='inbox@kylefuller.co.uk',
    url='http://github.com/rivrproject/rivr/',
    download_url='http://github.com/rivrproject/rivr/zipball/%s' % VERSION,
    packages=['rivr', 'rivr.middleware', 'rivr.views'],
    package_data={
        'rivr': ['py.typed'],
    },
    license='BSD',
    description='rivr is a microweb framework inspired by djng',
    long_description="rivr is a microweb framework inspired by djng, the reason I decided to create rivr and not use djng was that djng still depended on Django. I wanted rivr for places where I don't have Django. It is a lightweight framework which can be included along side another python application. rivr does not have a database layer, you are free to use whatever you choose.",
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Internet :: WWW/HTTP :: WSGI',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)


#!/usr/bin/env python

import os.path as op
from setuptools import setup, find_packages

def get_version(fname='autodoc/__init__.py'):
    with open(fname) as f:
        for line in f:
            if line.startswith('__version__'):
                return eval(line.split('=')[-1])


def read(fname):
    return open(op.join(op.dirname(__file__), fname)).read()


setup(
    name='autodoc',
    version=get_version(),
    description='Tool to validate and auto fix source code documentation.',
    long_description=read('README.rst'),
    author='Luddite Labs',
    author_email='autodoc@ludditelabs.io',
    url='http://autodoc.io',
    packages=find_packages(exclude=['tests']),
    license='',
    install_requires=[
        'click==6.7',
        'docutils==0.14',
        'PyYAML==3.13'
    ],
    entry_points={
        'console_scripts': ['autodoc=autodoc.cli:cli']
    },
    # TODO: set license.
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Topic :: Documentation",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Software Development :: Documentation",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Text Processing",
        "Topic :: Utilities",
    ]
)

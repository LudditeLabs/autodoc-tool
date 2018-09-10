#!/usr/bin/env python

import os.path as op
from setuptools import setup, find_packages


def get_version(fname='src/autodoc/__init__.py'):
    with open(fname) as f:
        for line in f:
            if line.startswith('__version__'):
                return eval(line.split('=')[-1])


def read(*parts, **kwargs):
    return open(op.join(op.dirname(__file__), *parts),
                encoding=kwargs.get('encoding', 'utf-8')).read()


setup(
    name='autodoc',
    version=get_version(),
    description='Tool to validate and auto fix source code documentation.',
    long_description=read('README.rst'),
    author='Luddite Labs',
    author_email='autodoc@ludditelabs.io',
    url='http://autodoc.io',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    zip_safe=True,
    license='',
    install_requires=[
        'click',
        'docutils',
        'PyYAML'
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

#!/usr/bin/env python

# Copyright 2018 Luddite Labs Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import os.path as op
from setuptools import setup, find_packages


def get_version(fname='src/autodoc/__init__.py'):
    with open(fname) as f:
        for line in f:
            if line.startswith('__version__'):
                return eval(line.split('=')[-1])


def read(*parts, **kwargs):
    return open(op.join(op.dirname(__file__), *parts)).read()


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
    license='Apache Software License',
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
        "License :: OSI Approved :: Apache Software License"
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

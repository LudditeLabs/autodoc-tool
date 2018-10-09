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

import sys
import os
import os.path as op
import platform
from datetime import datetime
import json
from sysconfig import get_python_version
from distutils import log
from distutils.command.bdist import bdist as _bdist
from distutils.command.bdist_dumb import bdist_dumb as _bdist_dumb
from distutils.dir_util import copy_tree, remove_tree
from cx_Freeze import setup, Executable


def get_version(filename='../src/autodoc/__init__.py'):
    with open(filename) as f:
        for line in f:
            if line.startswith('__version__'):
                return eval(line.split('=')[-1])


class BDistBase(_bdist_dumb):
    format = None

    def finalize_options(self):
        self.format = self.__class__.format
        if self.bdist_dir is None:
            bdist_base = self.get_finalized_command('bdist').bdist_base
            self.bdist_dir = os.path.join(bdist_base, self.format)
        _bdist_dumb.finalize_options(self)
        self.cmd = 'bdist_%s' % self.format

    def run(self):
        if not self.skip_build:
            self.run_command('build')

        pyversion = get_python_version()
        basename = "%s-%s-%s" % (self.distribution.get_fullname(),
                                 pyversion, self.plat_name)

        src_dir = self.get_finalized_command('build').build_exe
        dest_dir = op.join(self.bdist_dir, basename)

        if op.exists(dest_dir):
            remove_tree(dest_dir, verbose=0)
        copy_tree(src_dir, dest_dir, verbose=0)

        root = os.path.join(self.dist_dir, basename)
        filename = self.make_archive(root, self.format, root_dir=self.bdist_dir)
        self.create_metadata(filename, pyversion)
        if not self.keep_temp:
            remove_tree(self.bdist_dir, dry_run=self.dry_run)

    def create_metadata(self, bdist_filename, pyversion):
        outname = bdist_filename + '.meta'
        log.info('Creating package metadata %s', outname)

        arch = platform.architecture()[0]  # 32bit or 64bit
        os = platform.system().lower()

        meta_filename = '%s-%s-%s.meta.json' % (
            self.distribution.metadata.name, os, arch
        )

        meta = {
            'metadata_filename': meta_filename,
            'os': os,
            'arch': arch,
            'python': pyversion,
            'dist': op.basename(bdist_filename),
            'version': self.distribution.metadata.version,
            'timestamp': datetime.utcnow().isoformat(),
            'changes': [],  # release changes.
            'message': '',  # release message.
        }

        json.dump(meta, open(outname, 'w'), allow_nan=False, indent=4)


class BDistZip(BDistBase):
    description = 'create a ZIP distribution'
    format = 'zip'


class BDist(_bdist):
    def finalize_options(self):
        lst = [('bdist_zip', BDistZip)]
        for cmd, cls in lst:
            _, desc = self.format_command[cls.format]
            self.format_command[cls.format] = (cmd, desc)
        _bdist.finalize_options(self)


ext = '.exe' if os.name == 'nt' else ''
autodoc_filename = 'autodoc' + ext
contentdb_filename = 'contentdb' + ext

packages = ['site', 'docutils']
include_files = ['../src/contentdb/install/bin/%s' % contentdb_filename]
bin_includes = []

if sys.platform == 'linux':
    packages.append('_sysconfigdata_m_linux_x86_64-linux-gnu')
    bin_includes.extend(['libsqlite3.so.0', 'libstdc++.so.6', 'libz.so.1'])
    # system libs?
    # include_files.append('/lib/x86_64-linux-gnu/libpthread.so.0')
    # include_files.append('/lib/x86_64-linux-gnu/libm.so.6')
    # include_files.append('/lib/x86_64-linux-gnu/libgcc_s.so.1')
    # include_files.append('/lib/x86_64-linux-gnu/libc.so.6')


setup(name='autodoc',
      version=get_version(),
      description='Tool to validate and auto fix source code documentation.',
      author='Luddite Labs',
      author_email='autodoc@ludditelabs.io',
      url='https://autodoc.io',
      license='Apache Software License',
      cmdclass={
          'bdist': BDist,
          'bdist_zip': BDistZip
      },
      options={
          'build_exe': {
              'packages': packages,
              'excludes': ['tkinter'],
              'bin_includes': bin_includes,
              'include_msvcr': True,
              'path': sys.path + ['../src'],
              'include_files': include_files
          }
      },
      executables=[Executable('../src/autodoc/cli.py',
                              targetName=autodoc_filename)]
      )

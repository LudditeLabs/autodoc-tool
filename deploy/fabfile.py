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

import tempfile
import os
import os.path as op
from fabric import task
from invoke.exceptions import Exit
import json
import shutil

this_dir = op.abspath(op.dirname(__file__))
project_dir = op.abspath(op.join(this_dir, '..'))
dist_dir = op.abspath(op.join(this_dir, 'dist'))
testdata_dir = op.join(this_dir, 'testdata')


def _find_dist(platform):
    """Find distrib file for the given platform.

    Args:
        platform: Platform name.

    Returns:
        Absolute file path.
    """
    for entry in os.scandir(dist_dir):
        if not entry.name.endswith('.meta'):
            continue
        meta = json.load(open(entry.path))
        if meta['os'] == platform:
            return op.join(dist_dir, meta['dist'])
    raise Exit('Distrib for %s is not found in %s' % (platform, dist_dir),
               code=1)


@task(optional=['platform', 'tmp_dir'])
def build(c, platform='all', tmp_dir=None):
    """Build platform package."""
    builders = dict(linux=build_linux)

    if platform == 'all':
        names = builders.keys()
    else:
        if platform not in builders:
            raise Exit('Unknown platform: %s' % platform, code=1)
        names = [platform]

    if not tmp_dir:
        out_dir = tempfile.mkdtemp(prefix='autodoc-pkg-')
    else:
        out_dir = tmp_dir
    c.config['out_dir'] = out_dir

    if not op.exists(out_dir):
        os.makedirs(out_dir)

    if not op.exists(dist_dir):
        os.makedirs(dist_dir)

    pack_sources(c)

    for name in names:
        builder = builders.get(name)
        builder(c)

    # Cleanup only if temp dir is not passed explicitly.
    if not tmp_dir:
        shutil.rmtree(out_dir)


def pack_sources(c):
    """Pack sources and copy them to output directory."""
    # Based on:
    # https://minhajuddin.com/2016/01/10/how-to-get-a-git-archive-including-submodules/
    out_dir = c.config['out_dir']
    with c.cd(project_dir):
        filename = op.join(out_dir, 'autodoc-tool.tar')
        filename_sub = op.join(out_dir, 'autodoc-sub')

        c.run("git archive --verbose --format tar "
              "--output %s HEAD" % filename)

        c.run("git submodule foreach --recursive 'git archive --verbose "
              "--prefix=$path/ --format tar --output %s-$sha1.tar HEAD'"
              % filename_sub)

        res = c.run('ls %s-*' % filename_sub)
        for sub in res.stdout.strip().split('\n'):
            c.run('tar --concatenate --file %s %s' % (filename, sub))
        c.config['repo'] = filename


def build_linux(c):
    out_dir = op.join(c.config['out_dir'], 'linux')

    if op.exists(out_dir):
        shutil.rmtree(out_dir)
    os.makedirs(out_dir)

    with c.cd(out_dir):
        c.run('tar xf %s' % c.config['repo'])
        c.run('cp %s .' % op.join(this_dir, 'linux', 'build.sh'))
        if not op.exists(op.join(out_dir, 'deploy')):
            c.run('mkdir -p deploy')
            c.run('cp %s deploy/' % op.join(this_dir, 'cxsetup.py'))

    with c.cd(op.join(this_dir, 'linux')):
        c.run('docker build -t autodoc-tool-build .')

    c.run('docker run --rm -v %s:/project -e ASUID=%d autodoc-tool-build'
          % (out_dir, os.geteuid()))
    c.run('cp %s/deploy/dist/* %s' % (out_dir, dist_dir))

    test_linux(c)


def test_linux(c):
    out_dir = op.join(c.config['out_dir'], 'linux', 'test')

    filename = _find_dist('linux')
    name, _ = op.splitext(op.basename(filename))

    c.run('unzip -o %s -d %s' % (filename, out_dir))

    for image in c.config.build.linux.docker['test-images']:
        print('Test in %s...' % image)

        test_out_dir = op.join(out_dir, image)
        shutil.copytree(testdata_dir, test_out_dir)

        out = c.run('docker run --rm -e LC_ALL=C.UTF-8 -v {outdir}:/app '
                    '{image} /app/{exedir}/autodoc /app/{image}'.format(
            outdir=out_dir, exedir=name, image=image))

        if out.failed:
            raise Exit('Testing in %s... FAILED' % image, code=1)
        else:
            print('Testing in %s... OK' % image)

    print('Linux package testing is successfully finished!')

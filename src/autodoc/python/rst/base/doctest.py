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

"""
Doctest Blocks
--------------

Doctest blocks are text blocks which begin with ">>> ", the Python interactive
interpreter main prompt, and end with a blank line.

Doctest blocks are treated as a special case of literal blocks,
without requiring the literal block syntax.

If both are present, the literal block syntax takes priority
over Doctest block syntax.

http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html#doctest-blocks
"""


class DoctestMixin:
    def visit_doctest_block(self, node):
        self.open_block(top_margin=1, bottom_margin=1, no_wrap=True)

    def depart_doctest_block(self, node):
        self.close_block()

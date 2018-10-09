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
Literal Blocks
--------------

Syntax diagrams:

    +------------------------------+
    | paragraph                    |
    | (ends with "::")             |
    +------------------------------+
       +---------------------------+
       | indented literal block    |
       +---------------------------+


    +------------------------------+
    | paragraph                    |
    | (ends with "::")             |
    +------------------------------+
    +------------------------------+
    | ">" per-line-quoted          |
    | ">" contiguous literal block |
    +------------------------------+

http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html#literal-blocks
"""
from docutils import nodes


# Features:
# It tries to use fully minimized form.
# If in source code :: on a separate line then it will do the same.
class LiteralBlockMixin:
    quote_markers = '!"#$%&\'()*+,-./:;<=>?@[\]^_`{|}~'

    def __add_two_colons_block(self):
        self.open_block()
        self.block.add_boxed(u'::')
        self.close_block()

    def visit_literal_block(self, node):
        # Figure out where to place two colons.

        has_colons = False
        indent_detected = False

        if self.source_lines and node.line:
            # -1 to make it zero based
            pos = node.line - 1

            if self.source_lines[pos] and self.source_lines[pos][0] == ' ':
                indent_detected = True

            #  -2 to get line before the block
            pos -= 2
            line = self.source_lines[pos].strip()
            if line == '::':
                self.__add_two_colons_block()
                has_colons = True

        # If last line ends with a single ':' then add one more,
        # otherwise add separate block with '::'.
        if not has_colons and self.block_mgr.lines:
            last_line = self.block_mgr.lines[-1]

            if last_line[-1] == ':':
                self.block_mgr.lines[-1] = last_line + u':'
            else:
                self.__add_two_colons_block()

        indent = self.options['indent']
        self.open_block(indent=indent, top_margin=1,
                        bottom_margin=1, no_wrap=True)
        self.block.add_text(node.astext())

        # Additional check for Quoted Literal Blocks - contiguous blocks
        # where each line begins with the same non-alphanumeric character.
        #
        # block is LineBlock since we force no_wrap=True.
        # So we analyze lines.
        #
        # Take 1st char from each row in the block.
        # If they all starts with the same chan then compare with
        # allowed markers.
        # Also for empty lines we use space to prevent it from being
        # quoted block since each line must be marked.
        #
        # Do this only if indent is not detected.
        # This is because there may be quoted-like literal block with indent:
        #
        #     Bla bla::
        #
        #         > Some text
        #         > Some text2
        #
        if not indent_detected:
            start = set(x[0] if x else ' ' for x in self.block.lines)
            if len(start) == 1 and start.pop() in self.quote_markers:
                # Ok, seems it's an quoted block. Let's un indent it.
                # We don't care about width since we don't wrap.
                self.block.indent -= indent
        self.close_block()
        raise nodes.SkipNode

    def depart_literal_block(self, node):
        pass
        self.close_block()

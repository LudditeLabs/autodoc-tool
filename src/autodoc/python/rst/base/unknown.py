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
Unknown roles and directives
----------------------------

This module provides mixin which handles non-standard roles and directives
(not provided by the docutils out of the box or not registered by autodoc).

Notes:
    You have to enable unknown instructions support by calling
    :func:`autodoc.rst.roles.init` and :func:`autodoc.rst.directives.init`.
"""
from docutils import nodes


class UnknownMixin:
    def unknown_visit(self, node):
        # If it's something inline-like then process as role.
        if isinstance(node, nodes.Inline):
            self.visit_autodoc_unknown_role(node)
        else:
            # If block is opened then add content to it.
            if self.block:
                self.block.add_text(node.rawsource)
            # Otherwise add separate block.
            else:
                self.open_block(top_margin=1, bottom_margin=1)
                self.block.add_text(node.rawsource)
                self.close_block()
                raise nodes.SkipNode

    def unknown_departure(self, node):
        if isinstance(node, nodes.Inline):
            self.depart_autodoc_unknown_role(node)

    def visit_autodoc_unknown_role(self, node):
        if self.block:
            # Just use inline raw text.
            self.block.add_boxed(node.rawsource)
        raise nodes.SkipNode

    def depart_autodoc_unknown_role(self, node):
        pass

    # Common directive
    #
    #     .. <name>:: <param>
    #        <param>
    #
    #        <content>
    #
    #     .. <name>::
    #        <param>
    #
    #        <content>
    #
    #     .. <name>:: <content>
    #        <content>
    def visit_autodoc_unknown_directive(self, node):
        # Substitution definition.
        alt = node.get('alt')
        if alt is not None:
            prefix = u'.. |{}| {}::'.format(alt, node.tagname)
        else:
            prefix = u'.. {}::'.format(node.tagname)

        # If source code lines are passed then we check if next line is blank.
        if self.source_lines:
            # Zero based directive line is node.line - 1,
            # but we +1 to get next line, so result index will be node.line
            next_line_blank = not self.source_lines[node.line]
        else:
            next_line_blank = True

        # If directive has params then there can be two cases:
        #
        # First param on the same line (node.first_line_content = True):
        #
        #  .. <directive>: <param>
        #     <param>
        #
        # or on next line:
        #
        #  .. <directive>:
        #     <param>
        #     <param>
        #
        if node.params:
            # Directive opens text block to indent it's content.
            # Params opens separate text block and if
            # first param on the same line then we have to merge
            # it to the preceding block.
            if node.first_line_content:
                bottom_margin = None  # merge
            else:
                bottom_margin = 0

            self.open_block(top_margin=0, bottom_margin=bottom_margin,
                            child_indent=3)  # 3 = len('.. ')
            self.block.add_boxed(prefix)

            # If next line after directive is blank inthe original sources
            # then we do the same.
            if next_line_blank:
                bottom_margin = 1
            else:
                bottom_margin = 0

            # Tune first content block margin.
            if len(node.params) == 1 and node.first_line_content:
                top = 0
            else:
                top = 1

            self.open_block(top_margin=0, bottom_margin=bottom_margin,
                            next=dict(top_margin=top))

            # Add params.
            last = len(node.params) - 1
            for i, param in enumerate(node.params):
                # Add param and then force line break (except last one).
                self.block.add_boxed(param)
                if i != last:
                    self.block.add_boxed(u'\n')
            self.close_block()
        else:
            if node.first_line_content:
                bottom_margin = None
            else:
                bottom_margin = 0

            self.open_block(top_margin=0, bottom_margin=bottom_margin,
                            child_indent=3, next=dict(top_margin=0))
            self.block.add_boxed(prefix)

    def depart_autodoc_unknown_directive(self, node):
        self.close_block()

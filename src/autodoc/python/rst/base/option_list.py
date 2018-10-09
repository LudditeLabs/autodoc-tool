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
Options list
------------

http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html#option-lists
"""
from docutils import nodes


class OptionListMixin:
    def visit_option_list(self, node):
        self.states['opt_is_first'] = True
        self.states['opt_name_width'] = None

        # Save first option line to figure out indentation.
        if self.source_lines and node.line is not None:
            line = self.source_lines[node.line - 1]
            self.states['opt_first_line'] = line
        else:
            self.states['opt_first_line'] = None

    def depart_option_list(self, node):
        pass

    def visit_option_list_item(self, node):
        # Check if there are multiple paragraphs in description.
        self.states['opt_long_desc'] = len(node.children[1].children) > 1

    def depart_option_list_item(self, node):
        self.states['opt_long_desc_prev'] = self.states['opt_long_desc']
        self.close_block()

    def visit_option_group(self, node):
        self.states['opt_group'] = []

    def depart_option_group(self, node):
        # At this point we have list of options names in the
        # self.states['opt_group']. visit_option() populated it.
        # Make single string.
        group = self.states['opt_group']
        name = u', '.join(group)

        is_first_option = self.states.get('opt_is_first', False)
        self.states['opt_is_first'] = False

        bottom_margin = None

        # Force blank line for the first option to separate form other content.
        if is_first_option:
            top_margin = 1
        else:
            top_margin = self.options['opt_margin']
            top_margin = 1 if top_margin else None

        if (self.states['opt_long_desc']
            or self.states.get('opt_long_desc_prev')
            or self.states.get('opt_prev_need_margin')):
            top_margin = 1

        # If source line is available then we can detect description
        # indentation. It will be used for all subsequent options.
        # If such info is not available then we use 2-space indentation.
        if is_first_option:
            first_line = self.states.get('opt_first_line')
            if first_line is not None:
                last = group[-1]
                first_line = first_line.lstrip()
                width = first_line.index(last) + len(last)
                while first_line[width] == ' ':
                    width += 1
                self.states['opt_name_width'] = width
                self.states['opt_first_line'] = None
            else:
                last_width = self.block_mgr.last_width
                # If no info available then use fallback value.
                if last_width is None:
                    self.states['opt_name_width'] = 15
                # If width if available then calc reasonable option name width.
                else:
                    self.states['opt_name_width'] = last_width // 4

        next_opt = None
        name_width = self.states['opt_name_width']
        self.states['opt_prev_need_margin'] = False

        if name_width is not None:
            # If name is too long then we place description on next line
            # and separate whole option block with blank lines.
            if len(name) >= name_width:
                self.states['opt_prev_need_margin'] = True
                top_margin = 1
                bottom_margin = 0  # Overwrite None value to force line break.
                indent = name_width
                next_opt = dict(top_margin=0)
            else:
                name = name.ljust(name_width - 1)
                indent = len(name) + 1
        else:
            name += u' '
            indent = len(name) + 1

        # It will be closed in the depart_field() since we skip
        # depart_field_name().
        self.open_block(top_margin=top_margin, bottom_margin=bottom_margin,
                        child_indent=indent, next=next_opt)

        # This method is used to prevent blank line between blocks even if
        # previous block has bottom margin.
        # We ask to merge first line and make it empty.
        if top_margin is None:
            self.block.merge_to_new_line = True

        self.block.add_boxed(name)

    def visit_option(self, node):
        # <option><option_string>....</option_string></option>
        self.states['opt_group'].append(node.astext())
        raise nodes.SkipNode

    def depart_option(self, node):
        pass

    def visit_option_string(self, node):
        pass  # bullet

    def depart_option_string(self, node):
        pass

    def visit_option_argument(self, node):
        pass

    def depart_option_argument(self, node):
        pass

    def visit_description(self, node):
        pass  # body

    def depart_description(self, node):
        pass

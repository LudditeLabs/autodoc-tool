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
Definition list
---------------

http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html#definition-lists
"""
from ....docstring.utils import nop


class DefinitionList:
    visit_definition_list = nop
    depart_definition_list = nop

    def visit_definition_list_item(self, node):
        self.open_block(top_margin=1, child_indent=self.options['indent'],
                        next=dict(top_margin=0))

    def depart_definition_list_item(self, node):
        self.close_block()

    def visit_term(self, node):
        self.block.start_box()

    def depart_term(self, node):
        self.block.end_box()

    def visit_classifier(self, node):
        self.block.reopen_box()
        self.block.add_text(u' : ')

    def depart_classifier(self, node):
        self.block.end_box()
        pass

    def visit_definition(self, node):
        pass

    def depart_definition(self, node):
        pass

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
Comment block
-------------

"""
from docutils import nodes


class CommentMixin:
    def visit_comment(self, node):
        # Here we can pass indent as child_indent=3 or next=dict(indent=3, ...).
        # Difference is what child_indent will be inherited by all children
        # and 'next' indent will be ued only by first child and it's children.
        # In this case it's the same because we construct all blocks here.
        # We even can pass indent to the second open_block.
        self.open_block(top_margin=1, child_indent=3)
        self.block.add_boxed('..')
        self.open_block(top_margin=None, bottom_margin=1)
        self.block.add_text(node.rawsource)
        self.close_block()
        self.close_block()
        raise nodes.SkipNode

    def depart_comment(self, node):
        pass

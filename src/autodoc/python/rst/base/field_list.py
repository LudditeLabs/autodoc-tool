"""
Field list
----------

http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html#field-lists
"""
from docutils import nodes
from ....docstring.utils import nop


class FieldListMixin:
    def visit_field_list(self, node):
        # To control margin between fields.
        self.states['first_field'] = True

    depart_field_list = nop
    visit_field = nop

    def depart_field(self, node):
        # Opened in the visit_field_name()
        self.close_block()

    def visit_field_name(self, node):
        name = u':{}:'.format(node.astext())

        body_indent = self.options['field_body_indent']
        if body_indent is True:
            indent = len(name) + 1  # +1 for space
        elif body_indent is None:
            indent = self.options['indent']
        else:
            indent = body_indent

        # Force blank line for the first field to separate form other content.
        if self.states.get('first_field', False):
            top_margin = 1
            self.states['first_field'] = False
        else:
            #
            top_margin = self.options['field_margin']
            if top_margin is True:
                top_margin = 1
            elif not top_margin:
                top_margin = None

        # It will be closed in the depart_field() since we skip
        # depart_field_name().
        self.open_block(top_margin=top_margin, bottom_margin=None,
                        child_indent=indent)

        # Make sure we merge from new line.
        if top_margin is None:
            self.block.merge_to_new_line = True

        self.block.add_boxed(name)
        raise nodes.SkipNode

    def depart_field_name(self, node):
        pass

    def visit_field_body(self, node):
        if not node.children:
            self.open_block(bottom_margin=1)
            self.block.add_boxed('')
            self.close_block()

    def depart_field_body(self, node):
        pass

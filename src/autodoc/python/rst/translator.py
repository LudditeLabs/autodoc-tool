from .base import DocumentToRstTranslatorBase


class DocumentToRstTranslator(DocumentToRstTranslatorBase):
    """Translate docstring document to plan reStructuredText format."""

    def visit_docstring_section(self, node):
        if self.options.get('separate_info_fields'):
            self.open_block(top_margin=0, bottom_margin=0,
                            next=dict(top_margin=1))

    def depart_docstring_section(self, node):
        if self.options.get('separate_info_fields'):
            self.close_block()

    def visit_invisible_marker(self, node):
        self.open_block(top_margin=0, bottom_margin=1, next=dict(top_margin=1))

    def depart_invisible_marker(self, node):
        self.close_block()

    def _visit_common_info_field(self, node):
        section_name = node.parent['name']
        tag = (self.options.get('{}_tag'.format(section_name))
               or node['orig_field_tag'])

        parts = [tag]

        type_list = node.get('type')
        if type_list:
            parts += type_list

        n = node.get('name')
        if n:
            if n.startswith('*'):
                n = n.replace('*', r'\*')
            parts += [n]

        prefix = u':{}:'.format(u' '.join(parts))

        body_indent = self.options['field_body_indent']
        if body_indent is True:
            indent = len(prefix) + 1  # +1 for space
        elif body_indent is None:
            indent = self.options['indent']
        else:
            indent = body_indent

        top_margin = self.options['field_margin']
        if top_margin is True:
            top_margin = 1
        elif not top_margin:
            top_margin = None

        self.open_block(top_margin=top_margin, bottom_margin=None,
                        child_indent=indent)

        # Make sure we merge from new line.
        if top_margin is None:
            self.block.merge_to_new_line = True

        self.block.add_boxed(prefix)

    def _depart_common_info_field(self, node):
        self.close_block()

    def _visit_common_body(self, node):
        if not node.children:
            self.open_block(bottom_margin=1)
            self.block.add_boxed('')
            self.close_block()

    def _depart_common_body(self, node):
        pass

    visit_param_field = _visit_common_info_field
    depart_param_field = _depart_common_info_field
    visit_param_field_body = _visit_common_body
    depart_param_field_body = _depart_common_body

    visit_return_field = _visit_common_info_field
    depart_return_field = _depart_common_info_field
    visit_return_field_body = _visit_common_body
    depart_return_field_body = _depart_common_body

    visit_raises_field = _visit_common_info_field
    depart_raises_field = _depart_common_info_field
    visit_raises_field_body = _visit_common_body
    depart_raises_field_body = _depart_common_body

    def visit_yields_field(self, node):
        prefix = u':Yields:'

        body_indent = self.options['field_body_indent']
        if body_indent is True:
            indent = len(prefix) + 1  # +1 for space
        elif body_indent is None:
            indent = self.options['indent']
        else:
            indent = body_indent

        top_margin = self.options['field_margin']
        if top_margin is True:
            top_margin = 1
        elif not top_margin:
            top_margin = None

        self.open_block(top_margin=top_margin, bottom_margin=None,
                        child_indent=indent)

        # Make sure we merge from new line.
        if top_margin is None:
            self.block.merge_to_new_line = True

        self.block.add_boxed(prefix)

    depart_yields_field = _depart_common_info_field
    visit_yields_field_body = _visit_common_body
    depart_yields_field_body = _depart_common_body

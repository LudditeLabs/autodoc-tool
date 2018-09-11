from docutils import nodes
from ...docstring.nodes import docstring_section
from ..rst.translator import DocumentToRstTranslator


# http://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html
class DocumentToGoogleTranslator(DocumentToRstTranslator):
    def after_depart_document(self, document, lines):
        # Check if docstring starts with section and make sure there is a blank
        # line before it.
        if lines and lines[0]:
            sz = len(document)
            if sz == 1:
                i = 0
            elif sz > 1:
                i = 1
            else:
                i = None
            if i is not None and isinstance(document[i], docstring_section):
                name = document[i].get('name')
                if name in self.options['section_order']:
                    lines.insert(0, u'')
        return lines

    def get_section_title(self, name, node):
        """Get title of the section with the given name.

        It uses setting ``google_section_name_<name>`` if set or
        capitalized ``name``.

        Args:
            name: Section name.

        Returns:
            Section title.
        """
        if name == 'warning':
            return 'Warnings' if len(node) > 1 else 'Warning'
        elif name == 'seealso':
            return 'See Also'

        key = ('%s_label' % name).lower()
        value = self.options.get(key)
        return name.capitalize() if not value else value

    def visit_invisible_marker(self, node):
        # We don't use it here.
        raise nodes.SkipNode

    def visit_todo(self, node):
        indent = self.options['indent']
        self.open_block(top_margin=1, bottom_margin=0, child_indent=indent,
                        next=dict(top_margin=0))
        self.block.add_boxed('Todo:')

    def depart_todo(self, node):
        self.close_block()

    def visit_docstring_section(self, node):
        # Don't add section title if it has empty body or
        # skip_section_processing flag is set.
        if len(node) and not node.get('skip_section_processing'):
            title = self.get_section_title(node['name'], node) + u':'
            indent = self.options['indent']
            self.open_block(top_margin=1, bottom_margin=0, child_indent=indent,
                            next=dict(top_margin=0))
            self.block.add_boxed(title)

    def depart_docstring_section(self, node):
        if len(node) and not node.get('skip_section_processing'):
            self.close_block()

    def _visit_common_info_field(self, node):
        name = node.get('name')
        # No name - it's not a field.
        if name is None:
            # Here margins means nothing since the block will be empty.
            # we create it to propagate top_margin to the next block.
            self.open_block(next=dict(top_margin=0))
        else:
            type_list = node.get('type')
            if type_list:
                type_list = u', '.join(type_list)
                name += u' (' + type_list + u')'
            name += u':'

            indent = self.options['indent']
            # NOTES:
            #
            # * we use: top_margin=None + self.block.merge_to_new_line = True
            #   to always put the block to next line.
            #
            # * if top_margin=0 then fields will be separated by blank line.
            #
            # * bottom_margin=None - to merge next block to the line with the
            #   field name.
            #
            self.open_block(top_margin=None, bottom_margin=None,
                            child_indent=indent)
            self.block.merge_to_new_line = True
            self.block.add_boxed(name)

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

    def visit_return_field(self, node):
        type = node.get('type')
        self.open_block(next=dict(top_margin=None if type else 0))
        if type:
            self.block.add_boxed(u', '.join(type) + u':')

    depart_return_field = _depart_common_info_field
    visit_return_field_body = _visit_common_body
    depart_return_field_body = _depart_common_body

    def visit_raises_field(self, node):
        as_list = node.parent.get('as_list')
        type = node.get('type')
        # No name - it's not a field.
        if not type:
            # Here margins means nothing since the block will be empty.
            # we create it to propagate top_margin to the next block.
            if as_list:
                next = dict(top_margin=None, indent=2)  # 2 = len('* ')
            else:
                next = dict(top_margin=0)
            self.open_block(next=next)
            if as_list:
                self.block.add_boxed(u'*')
        else:
            type = u', '.join(type)
            if len(node.children[0]):
                type += u':'
            indent = self.options['indent']

            # NOTES:
            #
            # * we use: top_margin=None + self.block.merge_to_new_line = True
            #   to always put the block to next line.
            #
            # * if top_margin=0 then fields will be separated by blank line.
            #
            # * bottom_margin=None - to merge next block to the line with the
            #   field name.

            if as_list:
                params = dict(top_margin=0, bottom_margin=None, child_indent=2)
                type = u'* ' + type
            else:
                params = dict(top_margin=None, bottom_margin=None,
                              child_indent=indent)

            self.open_block(**params)
            self.block.merge_to_new_line = True
            self.block.add_boxed(type)

    depart_raises_field = _depart_common_info_field
    visit_raises_field_body = _visit_common_body
    depart_raises_field_body = _depart_common_body

    visit_yields_field = _visit_common_info_field
    depart_yields_field = _depart_common_info_field
    visit_yields_field_body = _visit_common_body
    depart_yields_field_body = _depart_common_body

    # This handler skips the node itself  and process only children.
    def _visit_admonition_without_directive(self, node):
        self.open_block(next=dict(top_margin=0))

    def _depart_admonition_without_directive(self, node):
        self.close_block()

    visit_seealso = _visit_admonition_without_directive
    depart_seealso = _depart_admonition_without_directive

    visit_note = _visit_admonition_without_directive
    depart_note = _depart_admonition_without_directive

    visit_warning = _visit_admonition_without_directive
    depart_warning = _depart_admonition_without_directive

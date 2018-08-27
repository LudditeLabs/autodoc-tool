from docutils import nodes
from ....docstring.transforms.field_sections import AddCollectedSectionsBase
from ....docstring.nodes import invisible_marker


class AddDocstringSections(AddCollectedSectionsBase):
    """Add collected sections back to the document."""
    def process_params(self, section):
        separate_type = self.env['settings'].get('separate_param_type', False)

        type_name = 'kwtype' if section.get('name') == 'keyword' else 'type'
        lst = section.children[:]
        sz = len(lst)

        for i, node in enumerate(reversed(lst)):
            type_spec = node.get('type')

            # This attr is set by the CollectInfoFields if type spec has spaces.
            has_complex_type = node.get('has_complex_type', False)

            need_separate = (
                    has_complex_type
                    or (type_spec is not None and len(type_spec) > 1)
                    or (separate_type and type_spec)
            )

            if need_separate:
                type_node = nodes.field()
                name_node = nodes.field_name(
                    text=u'{} {}'.format(type_name, node['name'])
                )
                type_node += name_node
                body = nodes.field_body()
                body += nodes.paragraph(text=u' or '.join(type_spec))
                type_node += body
                i = sz - i
                node.parent.insert(i, type_node)
                node.delattr('type')

    process_keyword = process_params

    def process_returns(self, section):
        lst = section.children[:]
        sz = len(lst)

        for i, node in enumerate(reversed(lst)):
            type_spec = node.get('type', [])
            node.delattr('type')
            for spec in type_spec:
                type_node = nodes.field()
                name_node = nodes.field_name(text='rtype')
                type_node += name_node
                body = nodes.field_body()
                body += nodes.paragraph(text=spec)
                type_node += body
                # Replace empty return field with :rtype:.
                if not len(node[0]):
                    node.parent.replace(node, type_node)
                else:
                    i = sz - i
                    node.parent.insert(i, type_node)

    def apply(self, **kwargs):
        for node in self.document.children:
            if isinstance(node, invisible_marker):
                self.add_sections(node)
                break
        else:
            # Add sections to the end of the document if marker is not present.
            sections = self.document.field_sections
            if len(sections):
                self.add_sections(self.document)

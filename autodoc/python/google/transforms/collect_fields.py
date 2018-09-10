from docutils import nodes
from ....docstring.nodes import seealso
from ....docstring.transforms.field_sections import CollectSectionsBase


class CollectGoogleSections(CollectSectionsBase):
    """Transform to collect google-style sections."""

    def __init__(self, *args, **kwargs):
        super(CollectGoogleSections, self).__init__(*args, **kwargs)
        self._to_remove = None

    def get_handler_name(self, node):
        # It can be Notes, Examples or References.
        if isinstance(node, nodes.admonition):
            if len(node) and isinstance(node[0], nodes.title):
                return node[0].astext()
        # It's a note.
        elif isinstance(node, nodes.note):
            return 'note'
        elif isinstance(node, seealso):
            return 'seealso'
        else:
            return node.tagname

    def add_to_section(self, section_name, node, remove_title=True,
                       unwrap=True):
        # This parent is used on deferred remove.
        node['real_parent'] = node.parent
        self.add_to_remove(node)

        section = self.get_docstring_section(section_name, node)
        if remove_title and isinstance(node[0], nodes.title):
            node.remove(node[0])
        if unwrap:
            section.extend(node.children)
        else:
            section += node
        return section

    def process_notes(self, node):
        self.add_to_section('notes', node)

    def process_note(self, node):
        self.add_to_section('note', node, unwrap=False)

    def process_examples(self, node):
        self.add_to_section('examples', node)

    def process_example(self, node):
        self.add_to_section('example', node)

    def process_references(self, node):
        self.add_to_section('references', node)

    def process_seealso(self, node):
        self.add_to_section('seealso', node, unwrap=False)

    def process_todo(self, node):
        section = self.add_to_section('todo', node, unwrap=False)
        # This means do nothing on section visit.
        # Sub nodes will do stuff.
        section['skip_section_processing'] = True

    def process_warning(self, node):
        self.add_to_section('warning', node, unwrap=False)

    def process_field_list(self, node):
        # Make a copy of children because there may be modifications.
        for el in node.children[:]:
            if not isinstance(el, nodes.field):
                continue

            # <field><field_name>...</field_name><field_body/></field>
            field_signature = el.children[0].children[0]

            if field_signature != 'Warns':
                continue

            self.add_to_section('warns', el, unwrap=False)

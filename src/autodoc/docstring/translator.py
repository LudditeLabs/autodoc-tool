from docutils import nodes
from ..textblock import BlockManager
from .utils import need_blank


class DocumentToTextTranslatorBase(nodes.NodeVisitor):
    """Base class for the document-to-text translators.

    This class is a document nodes visitor which translates docstring tree into
    text representation.

    It provides content blocks management and provides basic constructions
    parsing.
    """
    def __init__(self, document=None):
        """Construct translator.

        Args:
            document: RST document.
        """
        super(DocumentToTextTranslatorBase, self).__init__(document)
        self.output = None
        self.options = None
        self.source_lines = None
        self.num_source_lines = None
        self.block_mgr = None

        # States storage.
        # It used to store mixin specific data.
        self.states = dict()

    @property
    def block(self):
        """Current text block."""
        return self.block_mgr.block

    def open_block(self, indent=0, first_offset=None, child_indent=0,
                   top_margin=0, bottom_margin=0, no_wrap=False, next=None):
        self.block_mgr.open_block(indent, first_offset, child_indent,
                                  top_margin, bottom_margin, no_wrap, next)

    def close_block(self):
        self.block_mgr.close_block()

    def after_depart_document(self, document, lines):
        """Modify result lines after document is translated.

        Args:
            document: Docstring document.
            lines: List of result docstring lines.

        Returns:
            List of docstring lines.
        """
        return lines

    def postprocess_lines(self, lines):
        """Return result list of lines.

        This method performs final docstring lines modification.

        Args:
            lines: Document lines.

        Returns:
            List of lines.
        """
        lines = [x.rstrip() for x in lines]

        # Strip off trailing blank lines.
        while lines and not lines[-1]:
            lines.pop()

        # Strip off leading blank lines.
        while lines and not lines[0]:
            lines.pop(0)

        # Always add blank lines if docstring starts with non-anphanum char.
        # Side effect: blank lines will be added if global indent > 0,
        # because first line will start with space.
        force = lines and not lines[0][0].isalnum()

        # Prepend/append bank lines depending on options.
        # YES - Always add blank line.
        # AUTO - Add blank line if there are more than one line.
        if force or need_blank(self.options['first_blank_line'], lines):
            lines.insert(0, u'')
        if force or need_blank(self.options['last_blank_line'], lines):
            lines.append(u'')

        return lines

    # Reset state on new document.
    def visit_document(self, node):
        self.output = None

        self.options = node.env['settings']

        # Docstring lines are used to more accurate translation by referring
        # to original formatting.
        # Set by docstring.builder.DocumentBuilder
        self.source_lines = node.env['source_lines']
        self.num_source_lines = node.env['num_source_lines']

        self.block_mgr = BlockManager(
            indent=self.options['indent_global'],
            width=node.env.get('width'))

        self.states.clear()

    # Construct result docstring when document is processed.
    def depart_document(self, node):
        # Make sure all blocks are closed.
        self.block_mgr.close_all()

        lines = self.postprocess_lines(self.block_mgr.lines)

        # If there is only one line then make sure whole line (with quotes)
        # will fit to width.
        if len(lines) == 1 and self.block_mgr.width:
            extra = len(self.options['docstring_quote']) * 2
            self.block_mgr.clear()
            self.block_mgr.width -= extra
            self.open_block()
            self.block.add_text(lines[0])
            self.close_block()
            lines = self.postprocess_lines(self.block_mgr.lines)

        self.output = self.after_depart_document(node, lines)
        self.block_mgr.clear()
        self.options = None

    def visit_system_message(self, node):
        # We skip all messages.
        # They are collected in the document.parse_messages.
        raise nodes.SkipNode

    def depart_system_message(self, node):
        pass

    def visit_invisible_marker(self, node):
        raise nodes.SkipNode

    def depart_invisible_marker(self, node):
        pass

    # -- Text ----------------------------------------------------------------

    def visit_Text(self, node):
        self.block.add_text(node.astext())

    def depart_Text(self, node):
        pass

    # -- Paragraph -----------------------------------------------------------

    # TODO: don't ignore multiple lines between paragraphs.
    def visit_paragraph(self, node):
        # By default paragraphs are split with one blank line.
        # This may be overridden for complex nested constructions with
        # 'next' arg of the open_block().

        # Make sure first line fits to line width.
        first_offset = None
        quote = self.options.get("docstring_quote")
        if (quote and not self.block_mgr._blocks
                and not self.options["first_blank_line"]):
            first_offset = len(quote)
        self.open_block(top_margin=1, bottom_margin=1, first_offset=first_offset)

    def depart_paragraph(self, node):
        self.close_block()

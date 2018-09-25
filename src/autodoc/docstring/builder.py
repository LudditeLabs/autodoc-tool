from docutils.frontend import OptionParser
from docutils.parsers.rst import Parser
from .reader import TextReader


class DocumentBuilder:
    """This class builds docutils document using source reader and parser.

    Args:
        reader: Reader instance.
        parser: Parser instance.
        reader_cls: Reader class.
        parser_cls: Parser class.
        styles: List of :class:`DocstringStyle` instances. They used to
            pre-process input docstring text before converting to document.
    """

    def __init__(self, env, reader=None, parser=None, reader_cls=None,
                 parser_cls=None):
        self.env = env
        self.reader_cls = reader_cls or TextReader
        self.parser_cls = parser_cls or Parser
        self.reader = reader
        self.parser = parser
        self.setup_reader_and_parser()
        self.doc_settings = self._get_document_settings()

    def setup_reader_and_parser(self):
        """Create reader and parser instances if required."""
        if self.parser is None:
            self.parser = self.parser_cls()
        if self.reader is None:
            self.reader = self.reader_cls(self.parser)
        if self.reader.parser is None:
            self.reader.parser = self.parser
        self.parser = self.reader.parser

    def _get_document_settings(self):
        """Get settings for the docutils components."""
        components = (self.parser, self.reader)
        defaults = dict(read_config_files=False, report_level=5,
                        halt_level=10, warning_stream=False)
        opt_parser = OptionParser(components=components, defaults=defaults)
        return opt_parser.get_default_values()

    def parse(self, text, definition):
        # This 'env' will be attached to result document.
        self.reader.env = self.env
        document = self.reader.read(text, self.parser, self.doc_settings,
                                    source_path=definition.filename,
                                    encoding=self.env.get('input_encoding'))
        return document

    def get_document(self):
        definition = self.env['definition']

        text = definition.doc_block.docstring or ''

        document = self.parse(text, definition)

        # Make sure document has 'env' attached.
        if not hasattr(document, 'env'):
            document.env = self.env

        line_width = self.env['settings']['line_width']
        if line_width is not None:
            column = definition.get_start_pos()[1]
            # Make column zero-based.
            document.env['width'] = line_width - (column - 1)

        lines = text.splitlines()
        document.env['source_lines'] = lines
        document.env['num_source_lines'] = len(lines)

        return document

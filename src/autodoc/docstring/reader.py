from docutils.readers import Reader as _Reader
from docutils.io import StringInput
from functools import reduce


class Reader(_Reader):
    """This reader subscribes autodoc domain reporter on parser's messages."""
    def __init__(self, parser=None, parser_name=None):
        super(Reader, self).__init__(parser=parser, parser_name=parser_name)
        self.env = None

    def new_document(self):
        document = super(Reader, self).new_document()
        if self.env is not None and self.env['reporter'] is not None:
            document.reporter.attach_observer(
                self.env['reporter'].document_message)
        document.env = self.env
        return document

    def clear(self):
        self.env = None


class TextReader(Reader):
    """This reader accepts text as source."""
    def read(self, source, parser, settings, **params):
        source = StringInput(source=source, **params)
        return super(TextReader, self).read(source, parser, settings)

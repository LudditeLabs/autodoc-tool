from ...report import Codes
from .base import DocumentTransform


class MarkMissingDocstring(DocumentTransform):
    """This transform reports about missing or empty docstring.

    It also sets ``missing=True`` in ``document.env`` if docstring is
    missing.

    * Docstring is considered *missing* if it has no lines.
    * Docstring is considered *empty* if it has only blank lines lines.
    """

    def apply(self, **kwargs):
        definition = self.env['definition']
        if definition.doc_block.docstring is None:
            self.env['missing'] = True
            self.reporter.add_report(Codes.NODOC, 'Missing docstring.', 0, 0)
        elif not len(self.document):
            self.reporter.add_report(Codes.NODOC, 'Empty docstring.', 0, 0)

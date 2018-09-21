from ..domain import LanguageDomain
from ..task import SkipProcessing, DefinitionHandlerTask, FileSyncTask
from .rst import RstStyle
from .google import GoogleStyle
from .numpy import NumpyStyle
from ..docstring.transforms.missing_docstring import MarkMissingDocstring
from .rst.transforms.collect_fields import CollectInfoFields
from .rst.transforms.sync_params import SyncParametersWithSpec


class PyDefinitionHandlerTask(DefinitionHandlerTask):
    transforms = (MarkMissingDocstring, CollectInfoFields,
                  SyncParametersWithSpec)

    def setup(self):
        # NOTE: doxygen sets 'bodystart' to the line with colon, not to actual
        # body start as python's ast parser does::
        #
        #   def foo():  # <- bodystart
        #       pass
        #
        #   def foo(bla,
        #           bla2):  # <- bodystart
        #       pass
        #
        #   def foo()
        #       :  # <- bodystart
        #       pass
        #
        # Also 'bodyend' is set to line before next definition or EOL::
        #
        #   def foo():
        #       pass
        #               # <- bodyend
        #   def bar():
        #       pass    # <- bodyend
        #   def foo_1(): pass
        #               # <- bodyend
        #   def bar_1():
        #       pass

        super(PyDefinitionHandlerTask, self).setup()
        # This is one line function, skip processing.
        if self.definition.bodyend - self.definition.bodystart <= 1:
            raise SkipProcessing
        self.normalize_doc_block()

    def normalize_doc_block(self):
        doc = self.definition.doc_block
        if doc.id is None:
            doc.id_member = self.definition.id
            # TODO: detect kind
            doc.kind = 0                # 0:member 1:compound
            doc.id_file = self.definition.id_file
            doc.start_line = self.definition.bodystart
            # TODO: detect indent.
            doc.start_col = self.definition.start_col + 4
            doc.end_line = None
            doc.end_col = None


class PyFileSyncTask(FileSyncTask):
    def prepare(self, docblock):
        # Surround docstring with quotes.
        quote = self.settings['docstring_quote']
        docblock.docstring = quote + docblock.docstring + quote


class PythonDomain(LanguageDomain):
    name = 'python'
    extensions = ['.py', '.pyw']

    settings_section = 'py'
    settings_spec_help = 'Python language.'
    settings_spec = LanguageDomain.settings_spec + (
        ('Output docstring style.', 'style', 'rst'),
        ('Quote to use for docstrings.', 'docstring_quote', '"""'),
        (
            'List of sections in order of following in the docstring.',
            'section_order',
            [
                'todo',
                'example',
                'examples',
                'attributes',
                'params',
                'keyword',
                'returns',
                'raises',
                'yields',
                'methods',
                'warnings',
                'note',
                'notes',
                'seealso',
                'references',
            ]
        ),
    )

    settings_spec_nested = LanguageDomain.settings_spec_nested + (
        RstStyle, GoogleStyle, NumpyStyle
    )

    docstring_styles = (RstStyle, GoogleStyle, NumpyStyle)

    definition_handler_task = PyDefinitionHandlerTask
    file_sync_task = PyFileSyncTask

    def __init__(self):
        super(PythonDomain, self).__init__()

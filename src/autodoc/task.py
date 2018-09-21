from functools import reduce
from docutils.transforms import Transformer
from .settings import SettingsSpec
from .docstring.builder import DocumentBuilder
from .patch import Patch, FilePatcher


class SkipProcessing(Exception):
    pass


class BaseTask(SettingsSpec):
    """Base class for the autodoc tasks."""
    def __init__(self, domain, env):
        """Create task.

        Args:
            domain: :class:`LanguageDomain` instance.
            env: Processing environment dict.
        """
        self.domain = domain
        self.env = env
        self.settings = env['settings']

    def setup(self):
        """Setup task."""
        pass

    def teardown(self):
        """Tear down task."""
        self.env = None
        self.domain = None

    def do_run(self):
        """Entry point for subclasses."""
        raise NotImplementedError

    def run(self):
        """Run task.

        This method calls the following methods:

        * :meth:`setup`.
        * :meth:`do_run`.
        * :meth:`teardown`.

        """
        self.setup()
        self.do_run()
        self.teardown()


class DefinitionHandlerTask(BaseTask):
    """Base task for the definition handlers.

    "Definition" represents some entity like function, class, method etc.
    """

    #: Document builder class.
    document_builder = DocumentBuilder

    #: Document transforms.
    transforms = None

    def __init__(self, domain, env):
        """Create handler.

        Args:
            domain: :class:`LanguageDomain` instance.
            env: Processing environment dict.
        """
        super(DefinitionHandlerTask, self).__init__(domain, env)
        self.definition = self.env['definition']

    def apply_styles(self):
        """Apply styles transforms to docstring before document building.

        This method applies the transforms only if docstring exists and document
        tree is not prebuilt.
        """
        doc_block = self.definition.doc_block
        if doc_block.docstring is not None and doc_block.document is None:
            text = doc_block.docstring
            text = reduce(lambda t, f: f(t, self.env),
                          self.domain._styles_transforms, text)
            doc_block.docstring = text

    def build_document(self):
        """Build document tree from the docstring stored in the ``env``.

        This method puts document tree to``definition.doc_block.document``.
        """
        self.apply_styles()
        # Don't parse docstring if document tree already present
        # (if document is already present in the content DB).
        if self.definition.doc_block.document is None:
            builder = self.document_builder(self.env)
            self.definition.doc_block.document = builder.get_document()

    def apply_transforms(self):
        """Apply transforms on current document tree."""
        if self.transforms:
            transformer = Transformer(self.definition.doc_block.document)
            transformer.add_transforms(self.transforms)
            transformer.apply_transforms()

    def translate_document_to_docstring(self):
        """Translate document tree to text representation using style specified
        in the ``env['settings']['style']`` and update ``definition``.

        Translation is performed by style specified in settings.
        """
        style_name = self.settings['style']
        style = self.domain.get_style(style_name)
        assert style is not None
        self.definition.doc_block.docstring = style.to_string(self.env)

    def save_changes(self):
        """Save changes made by the handler to content DB."""
        self.env['db'].save_doc_block(self.definition)

    def do_run(self):
        self.build_document()
        self.apply_transforms()
        self.translate_document_to_docstring()
        self.save_changes()


class FileSyncTask(BaseTask):
    """Base class for the file sync tasks.

    This task takes content from DB, creates a patch and applies it to
    destination file.
    """
    def __init__(self, domain, env):
        super(FileSyncTask, self).__init__(domain, env)
        self.file_id = self.env['file_id']
        self.filename = self.env['filename']
        self.patcher = None

    def setup(self):
        """Setup file patcher."""
        super(FileSyncTask, self).setup()
        self.patcher = FilePatcher(self.filename)

    def teardown(self):
        """Save modifications to file."""
        filename = self.env.get('out_filename') or self.filename
        self.patcher.patch(filename)
        self.patcher = None
        super(FileSyncTask, self).teardown()

    def prepare(self, docblock):
        """Prepare ``docblock`` for patching.

        Args:
            docblock: :class:`DocBlock` instance.
        """
        pass

    def do_run(self):
        """Go over all docblocks for a specified file and create patches."""
        for docblock in self.env['db'].get_doc_blocks(self.file_id):
            self.prepare(docblock)
            if docblock.docstring is not None:
                patch = Patch(docblock.docstring, docblock.start_line,
                              docblock.start_col, docblock.end_line,
                              docblock.end_col)
                self.patcher.add(patch)

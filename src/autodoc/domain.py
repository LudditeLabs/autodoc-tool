from functools import reduce
from docutils.transforms import Transformer
from .report import DomainReporter
from .settings import SettingsSpec
from .docstring.builder import DocumentBuilder
from .patch import Patch, FilePatcher


class SkipProcessing(Exception):
    pass


class BaseHandler(SettingsSpec):
    """Base class for handlers."""
    def __init__(self, domain, env):
        """Create handler.

        Args:
            domain: :class:`LanguageDomain` instance.
            env: Processing environment dict.
        """
        self.domain = domain
        self.env = env
        self.settings = env['settings']

    def setup(self):
        """Setup handler."""
        pass

    def teardown(self):
        """Tear down handler."""
        self.env = None
        self.domain = None

    def do_handle(self):
        raise NotImplementedError

    def handle(self):
        self.setup()
        self.do_handle()
        self.teardown()


class DefinitionHandler(BaseHandler):
    """Base class for the definition handlers.

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
        super(DefinitionHandler, self).__init__(domain, env)
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
        style_name = self.env['settings']['style']
        style = self.domain.get_style(style_name)
        assert style is not None
        self.definition.doc_block.docstring = style.to_string(self.env)

    def save_changes(self):
        """Save changes made by the handler to content DB."""
        self.env['db'].save_doc_block(self.definition)

    def do_handle(self):
        self.build_document()
        self.apply_transforms()
        self.translate_document_to_docstring()
        self.save_changes()


class LanguageDomain(SettingsSpec):
    #: Domain name (language).
    #:
    #: It used as a display name in the reports and also it defines
    #: source language name.
    name = None

    #: Supported files extensions.
    extensions = None

    settings_spec = (
        ('Input docstring style.', 'instyle', 'all'),

        ('Docstring width.', 'line_width', 80, (None, int)),
        ('Default indentation for nested constructions.', 'indent', 4),
        ('Entire docstring indentation.', 'indent_global', 0),

        (
            """
            Make sure first line is blank.
            None means have blank line only for multi line docstring.
            False - no blank lines
            True - add single blank line
            <num> - number of blank lines.
            """,
            'first_blank_line', False, (None, bool, int)
        ),

        (
            """
            Make sure last line is blank.
            None means have blank line only for multi line docstring.
            False - no blank lines
            True - add single blank line
            <num> - number of blank lines.
            """,
            'last_blank_line', None, (None, bool, int)
        ),

        # For example:
        #     :strong:`strong` -> **strong**
        #     :title-reference:`Title ref` -> :t:`Title ref`
        ('Use shorter version of the inline markup.', 'shorten_inline', True),

        (
            """
            Number of lines to add to empty/missing docstring.
            Zero means remove empty docstring.
            """,
            'empty_docstring_lines', 0
        ),
    )

    definition_handler = None
    docstring_styles = None

    def __init__(self):
        self.reporter = DomainReporter(self)
        self.context = None

        lst = self.docstring_styles or []
        self._styles = [x(self) for x in lst]
        self._styles_map = {x.name: x for x in self._styles}
        self._styles_transforms = [x.transform_docstring for x in self._styles]

    @property
    def logger(self):
        return self.context.logger

    @property
    def settings(self):
        return self.context.settings

    @property
    def styles(self):
        """List of styles instances.

        The list is built from list of style classes in
        :attr:`docstring_styles`.
        """
        return self._styles

    def get_style(self, name):
        """Get style by name.

        Args:
            name: Style name.

        Returns:
            :class:`DocstringStyle` instance or ``None``.
        """
        return self._styles_map.get(name)

    def create_env(self, content_db, **kwargs):
        """Create processing environment dict.

        Args:
            content_db: Content DB instance.
            **kwargs: Extra env vars.

        Returns:
            Processing environment dict.
        """
        env = {
            'db': content_db,
            'reporter': self.reporter,
            'settings': self.settings,
        }
        env.update(kwargs)
        return env

    def create_definition_handler(self, env):
        return self.definition_handler(self, env)

    def process_definition(self, content_db, definition):
        with self.settings.from_key('style'):
            env = self.create_env(content_db, definition=definition)
            self.reporter.env = env
            handler = self.create_definition_handler(env)

            try:
                handler.handle()
            except SkipProcessing:
                pass

            self.reporter.reset()

    def prepare_to_sync(self, docblock):
        pass

    def sync_sources(self, content_db):
        """Sync sources with content in the given DB.

        Args:
            content_db: Content DB instance.
        """

        with self.settings.from_key('style'):
            for id, filename in content_db.get_domain_files(self):
                patcher = FilePatcher(filename)

                # Create patches.
                for docblock in content_db.get_doc_blocks(id):
                    self.prepare_to_sync(docblock)
                    if docblock.docstring is not None:
                        patch = Patch(docblock.docstring, docblock.start_line,
                                      docblock.start_col, docblock.end_line,
                                      docblock.end_col)
                        patcher.add(patch)

                patcher.patch()

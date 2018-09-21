from .contentdb import ContentDbBuilder, ContentDb
from .settings import SettingsSpec


class Context(SettingsSpec):
    """Autodoc context.

    Args:
        logger: Logger instance.
    """
    def __init__(self, logger):
        super(Context, self).__init__()
        self.logger = logger
        self.settings = None
        self.domains = {}
        self.settings_spec_nested = []

    def register(self, domain):
        """Register language domain.

        Args:
            domain: :class:`LanguageDomain` instance.
        """
        if domain.name in self.domains:
            raise ValueError('Already registered: %s' % domain.name)
        self.domains[domain.name] = domain
        domain.context = self
        self.settings_spec_nested.append(domain)

    def build_content_db(self, filename, paths, exclude, exclude_patterns, exe):
        """Build content DB for the given paths.

        Args:
            filename: Output content DB filename.
            paths: Paths to process.
            exclude: List of paths to exclude.
            exclude_patterns: List of patterns to exclude.
            exe: External executable to build content DB.

        Returns:
            :class:`ContentDb` instance.
        """
        db_builder = ContentDbBuilder(self, exe=exe)

        # Process files supported by registered domains only.
        file_patterns = []
        for domain in self.domains.values():
            if domain.extensions:
                file_patterns.extend(['*' + x for x in domain.extensions])

        return db_builder.build(filename, paths, exclude=exclude,
                                exclude_patterns=exclude_patterns,
                                file_patterns=file_patterns)

    def get_content_db(self, filename):
        """Construct :class:`ContentDb` for the given filename.

        Args:
            filename: Content DB filename.

        Returns:
            :class:`ContentDb` instance.
        """
        return ContentDb(self, filename)

    def analyze(self, content_db):
        """Analyse given content DB.

        Args:
            content_db: :class:`ContentDb` instance.
        """
        for definition in content_db.get_definitions():
            domain = self.domains.get(definition.language)
            if domain is not None:
                with self.settings.with_settings(domain.settings_section):
                    domain.process_definition(content_db, definition)

    def sync_sources(self, content_db, out_filename=None):
        """Sync sources with content in the given DB.

        Args:
            content_db: Content DB instance.
            out_filename: Output filename. Ignored if there are multiple files
                to sync.
        """
        # If there are multiple files to sync then ignore this filename.
        # NOTE: temporary disabled until better SQL query.
        # if out_filename:
        #     if content_db.get_files_count():
        #         out_filename = None

        for lang in content_db.get_languages():
            domain = self.domains.get(lang)
            if domain is not None:
                with self.settings.with_settings(domain.settings_section):
                    domain.sync_sources(content_db, out_filename)

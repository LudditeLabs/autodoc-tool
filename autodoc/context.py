from .contentdb import ContentDbBuilder, ContentDb
from .settings import SettingsSpec


class Context(SettingsSpec):
    """Autodoc context.

    Args:
        logger: Logger instance.
    """
    def __init__(self, logger):
        super(SettingsSpec, self).__init__()
        self.logger = logger
        self.settings = None
        self.domains = {}
        self.settings_spec_nested = []

    def register(self, domain):
        if domain.name in self.domains:
            raise ValueError('Already registered: %s' % domain.name)
        self.domains[domain.name] = domain
        domain.context = self
        self.settings_spec_nested.append(domain)

    def build_content_db(self, filename, paths, exclude, exclude_patterns,
                         builder):
        db_builder = ContentDbBuilder(self.logger, exe=builder)
        return db_builder.build(filename, paths, exclude=exclude,
                                exclude_patterns=exclude_patterns)

    def get_content_db(self, filename):
        return ContentDb(filename)

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

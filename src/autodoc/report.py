import logging
from docutils.utils import Reporter as _Reporter


def create_logger(verbose=False):
    """Create autodoc logger.

    This function creates output stream logger with simplified message format.

    Args:
        verbose: Set debug level.

    Returns:
        Logger instance.
    """
    console = logging.StreamHandler()
    console.setFormatter(logging.Formatter('%(message)s'))
    logger = logging.getLogger('autodoc')
    logger.addHandler(console)
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)
    return logger


# Levels mapping to convert from docutils levels to logging levels.
_levels = {
    _Reporter.DEBUG_LEVEL: logging.DEBUG,
    _Reporter.INFO_LEVEL: logging.INFO,
    _Reporter.WARNING_LEVEL: logging.WARNING,
    _Reporter.ERROR_LEVEL: logging.ERROR,
    _Reporter.SEVERE_LEVEL: logging.FATAL
}


class Codes(object):
    """Report codes."""

    # -- Docstring analysis codes ---------------------------------------------

    #: Something is too complex (like 'specification too complex').
    COMPLEX = 'D301'

    #: Duplicate (duplicate declaration).
    DUPLICATE = 'D302'

    #: Something is incorrect (incorrect signature).
    INCORRECT = 'D303'

    #: Something unknown.
    UNKNOWN = 'D304'

    #: Empty state.
    EMPTY = 'D305'

    #: Missing state.
    MISSING = 'D306'

    #: Mismatch in something.
    MISMATCH = 'D307'

    #: Empty/missing docstring.
    NODOC = 'D308'

    #: Docstring parsing error.
    PARSERR = 'D309'

    # -- Other codes ----------------------------------------------------------

    #: Internal errors.
    INTERNAL = 'INTERNAL'

    #: Information.
    INFO = 'D300'

    #: Transform errors.
    ERROR = 'D401'

    #: I/O errors.
    IOERROR = 'D402'


class BaseReporter:
    def __init__(self):
        self.definition = None

    def reset(self):
        """Reset reporter's state."""
        self.definition = None

    def document_message(self, msg):
        """This method collects docutils' reporter messages."""
        if self.definition is not None:
            line, col = self.definition.get_start_pos()
        else:
            line = col = None

        if msg.hasattr('autodoc'):
            self.add_report(msg.get('code', 'D201'), msg.children[0].astext(),
                            line, col)
        else:
            level = msg.get('level')
            log_level = _levels.get(level, logging.DEBUG)
            code = 'D1{:02d}'.format(level)
            text = msg.children[0].astext().replace('\n', ' ')
            self.add_report(code, text, line, col, log_level)

    def add_report(self, code, message, line=None, col=None, level=None):
        """Add report.

        Args:
            code: Report code.
            message: Report message.
            line: Line number in the content.
            col:  Column number in the content.
            level: Logging level. Info level is used if not specified.
        """
        pass


class DomainReporter(BaseReporter):
    #: Message format.
    fmt = u'{path}: [{code}] {msg}'

    def __init__(self, domain):
        super(DomainReporter, self).__init__()
        self.domain = domain
        self._env = None
        self._filename = None

    @property
    def env(self):
        return self._env

    @env.setter
    def env(self, value):
        self._env = value
        self.definition = value['definition']
        self._filename = self.definition.filename

    def reset(self):
        super(DomainReporter, self).reset()
        self._filename = None
        self._env = None

    def add_report(self, code, message, line=0, col=0, level=None):
        level = level or logging.INFO
        if self.definition is not None:
            line_, col_ = self.definition.get_start_pos()
            if line == 0:
                line = line_
            if col == 0:
                col = col_
            name = self.definition.name
        else:
            name = None

        path_item = [self._filename] if self._filename else []

        if line is not None:
            # NOTE:
            # We +1 because all indexes and positions are assumed to be
            # zero-based and we display in 1-based format.
            path_item.append(str(line))
            path_item.append(str(col))

        code_item = [code, self.domain.name]
        if name:
            code_item.append(name)

        message = self.fmt.format(path=':'.join(path_item),
                                  code=':'.join(code_item), msg=message)

        self.domain.logger.log(level, message)

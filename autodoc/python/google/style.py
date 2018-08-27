from ...report import Codes
from ...settings import C
from ..style_napoleon import NapoleonStyleTransform, NapoleonStyle
from ...utils import get_indent
from ..napoleon import GoogleDocstring
from .translator import DocumentToGoogleTranslator


class FromGoogleStyleTransform(NapoleonStyleTransform):
    """Convert Google style docstrings to reStructuredText."""

    name = 'google'
    converter = GoogleDocstring

    def __init__(self, reporter):
        super(FromGoogleStyleTransform, self).__init__(reporter)
        self.cfg.napoleon_google_docstring = True
        self.sections = {
            'args': self._sanitize_remove_section,
            'arguments': self._sanitize_remove_section,
            'attributes': self._sanitize_remove_section,
            'example': self._sanitize_remove_section,
            'examples': self._sanitize_remove_section,
            'keyword args': self._sanitize_remove_section,
            'keyword arguments': self._sanitize_remove_section,
            'methods': self._sanitize_remove_section,
            'note': self._sanitize_remove_section,
            'notes': self._sanitize_remove_section,
            'other parameters': self._sanitize_remove_section,
            'parameters': self._sanitize_remove_section,
            'return': self._sanitize_remove_section,
            'returns': self._sanitize_remove_section,
            'raises': self._sanitize_remove_section,
            'references': self._sanitize_remove_section,
            'see also': self._sanitize_remove_section,
            'todo': self._sanitize_remove_section,
            'warning': self._sanitize_remove_section,
            'warnings': self._sanitize_remove_section,
            'warns': self._sanitize_remove_section,
            'yield': self._sanitize_remove_section,
            'yields': self._sanitize_remove_section,
        }

    def _sanitize_remove_section(self, lines, pos):
        msg = 'Empty section [%s]' % lines[pos][:-1]
        self.reporter.add_report(Codes.EMPTY, msg, line=0, col=0)
        lines[pos] = u''

    def sanitize(self, lines, has_sections):
        sz = len(lines)
        # Go over lines in reversed mode and find empty sections.
        # Empty section is a section without a content:
        #
        #    Returns:
        #
        #    <text>
        #
        # Such sections will be modified or removed.
        for i, line in enumerate(reversed(lines), start=1):
            if not line.endswith(':'):
                continue
            name = line[:-1].lower()
            func = self.sections.get(name)
            if func is not None and self.is_section_empty(lines, sz - i, sz):
                func(lines, sz - i)
        return lines

    def is_section_empty(self, lines, pos, size):
        is_empty = True
        section_indent = get_indent(lines[pos])
        pos += 1
        while pos < size:
            line = lines[pos]
            if line:
                indent = get_indent(line)
                if indent > section_indent:
                    is_empty = False
                    break
            pos += 1

        return is_empty


# TODO: collect other sections.
class GoogleStyle(NapoleonStyle):
    """Pipeline to translate docstring document to Google style format."""

    name = 'google'

    settings_section = name
    settings_spec_help = 'Google docstring style.'
    settings_spec = (
        ('Params section', 'params_label', 'Args',
         C('Args', 'Arguments', 'Parameters')),

        ('Returns section', 'returns_label', 'Returns',
         C('Return', 'Returns')),

        ('Raises section', 'raises_label', 'Raises', C('Raise', 'Raises')),
    )

    document_translator_cls = DocumentToGoogleTranslator
    docstring_transform_cls = FromGoogleStyleTransform

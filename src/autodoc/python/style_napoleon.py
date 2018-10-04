from .napoleon import Config
from .rst.style import RstBaseStyle
from ..contentdb import DefinitionType, MemberType


class NapoleonStyleTransform:
    """Base class for converters from google and numpy styles to
    reStructuredText.

    Converter takes docstring in one of above format and converts it to
    reStructuredText docstring.

    Notes:
        Based on modified version of the :mod:``sphinx.ext.napoleon``.

    See Also:
        :class:`~..pipeline.unit.DocStylePipeline`.
    """

    #: Class to use for converting a style to reStructuredText.
    converter = None

    def __init__(self, reporter):
        self.reporter = reporter
        self.cfg = Config()
        self.cfg.napoleon_google_docstring = False
        self.cfg.napoleon_numpy_docstring = False
        self.cfg.napoleon_use_admonition_for_examples = True
        self.cfg.napoleon_use_admonition_for_notes = True
        self.cfg.napoleon_use_admonition_for_references = True
        self.cfg.napoleon_use_ivar = True

    def sanitize(self, lines, has_sections):
        """Sanitize result reStructuredText if required.

        Args:
            lines: Docstring lines in the reStructuredText format.

        Returns:
            Sanitized list of docstring lines.
        """
        return lines

    def convert(self, text, definition_name=None, definition_type=None):
        """Convert input docstring to reStructuredText.

        Args:
            text: Docstring as text or list of lines.
            definition_name: The fully qualified name of the documented node.
            definition_type: A string specifying the type of the object to which
                the docstring belongs. Valid values: "module", "class",
                 "exception", "function", "method", "attribute".

        Returns:
            str: Docstring in reStructuredText format.
        """
        p = self.converter(text, self.cfg, name=definition_name,
                           what=definition_type)
        lines = self.sanitize(p.lines(), p.has_sections)
        return '\n'.join(lines)


class NapoleonStyle(RstBaseStyle):
    """Pipeline to translate docstring document to Google style format."""

    docstring_transform_cls = None

    def __init__(self, domain):
        super(NapoleonStyle, self).__init__(domain)
        self._transform = self.docstring_transform_cls(domain.reporter)

    def get_definition_type(self, definition):
        """Helper method to get definition type name."""
        if definition.type is DefinitionType.MEMBER:
            if definition.is_method:
                return 'method'
            elif definition.is_function:
                return 'function'
            elif definition.kind in (MemberType.VARIABLE, MemberType.PROPERTY):
                return 'attribute'
        elif definition.type is DefinitionType.CLASS:
            return 'class'

        # By default it's function.
        return 'function'

    def transform_docstring(self, text, env):
        definition = env['definition']
        definition_type = self.get_definition_type(definition)
        return self._transform.convert(text, definition.name, definition_type)

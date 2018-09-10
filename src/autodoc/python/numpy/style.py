from ..style_napoleon import NapoleonStyleTransform, NapoleonStyle
from ..napoleon import NumpyDocstring
from .translator import DocumentToNumpyTranslator


# TODO: implement me.
class FromNumpyStyleTransform(NapoleonStyleTransform):
    """Convert NumPy style docstrings to reStructuredText."""

    name = 'numpy'
    converter = NumpyDocstring

    def __init__(self, reporter):
        super(FromNumpyStyleTransform, self).__init__(reporter)
        self.cfg.napoleon_numpy_docstring = True

    # TODO: implement me
    def sanitize(self, lines, has_sections):
        return lines


class NumpyStyle(NapoleonStyle):
    """Pipeline to translate docstring document to Google style format."""

    name = 'numpy'

    settings_section = name
    settings_spec_help = 'NumPy docstring style.'

    document_translator_cls = DocumentToNumpyTranslator
    docstring_transform_cls = FromNumpyStyleTransform

from docutils.transforms import Transformer
from docutils.io import StringOutput
from .settings import SettingsSpec
from .docstring.writer import TextWriter


class DocstringStyle(SettingsSpec):
    """This class represents docstring style.

    It converts document tree to text representation and also transforms
    input docstring text to common format which is used to build document tree.
    """

    #: Style name.
    name = None

    #: Document-to-text translator class.
    document_translator_cls = None

    #: List of document tree transforms.
    #:
    #: They applied before translating the tree to text.
    #:
    #: See Also:
    #:    :meth:`transform_document`, :meth:`to_string`.
    transforms = None

    def __init__(self, domain):
        """Construct a style.

        Args:
            domain: :class:`LanguageDomain` instance.
        """
        self.domain = domain

    def transform_document(self, document):
        """Apply transforms to the given ``document``.

        Args:
            document: Document tree.

        See Also:
            :attr:`transforms`.
        """
        if self.transforms:
            transformer = Transformer(document)
            transformer.add_transforms(self.transforms)
            transformer.apply_transforms()

    def to_string(self, env):
        """Convert document tree in the ``env`` to text representation.

        Args:
            env: Processing environment dict.

        Returns:
            str: Text representation of the document.
        """
        document = env['definition'].doc_block.document
        self.transform_document(document)

        out = StringOutput(encoding=env.get('input_encoding', 'utf-8'))
        writer = TextWriter(self.document_translator_cls)
        writer.write(document, out)
        return out.destination

    def transform_docstring(self, text, env):
        """Transform given text.

        This method is called by the :class:`DocumentBuilder` to prepare input
        docstring for building document tree.

        Args:
            text: Docstring text.
            env: Processing environment dict.

        Returns:
            str: Transformed docstring text.
        """
        return text

from docutils import nodes
from docutils.transforms import Transform
from ....docstring.translator import DocumentToTextTranslatorBase
from .inline import InlineMixin
from .comment import CommentMixin
from .admonition import AdmonitionMixin
from .section import SectionMixin
from .list import ListMixin
from .definition_list import DefinitionList
from .field_list import FieldListMixin
from .option_list import OptionListMixin
from .literal_block import LiteralBlockMixin
from .line_block import LineBlockMixin
from .block_quote import BlockQuoteMixin
from .doctest import DoctestMixin
from .unknown import UnknownMixin


class StripMessages(Transform):
    """Remove all system messages from the document."""

    # docutils.transforms.universal.FilterMessages has 870.
    # 0 - highest priority, 999 - lowest.
    # We want to be applied before FilterMessages.
    default_priority = 869

    def apply(self):
        for node in self.document.traverse(nodes.system_message):
            node.parent.remove(node)


# TODO: Footnote references is not supported.
# TODO: Citation references is not supported.
class DocumentToRstTranslatorBase(UnknownMixin, InlineMixin, CommentMixin,
                                  AdmonitionMixin, SectionMixin, ListMixin,
                                  DefinitionList, FieldListMixin,
                                  OptionListMixin, LiteralBlockMixin,
                                  LineBlockMixin, BlockQuoteMixin, DoctestMixin,
                                  DocumentToTextTranslatorBase):
    """This class translates document to the reStructuredText."""
    pass

# Copyright 2018 Luddite Labs Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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

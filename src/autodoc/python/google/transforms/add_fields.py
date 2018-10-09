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
from ....docstring.transforms.field_sections import AddCollectedSectionsBase


class AddDocstringSections(AddCollectedSectionsBase):
    """Add collected sections back to the document."""

    def process_raises(self, section):
        # If type is not set then we construct a list of exceptions.
        # See DocumentToGoogleStyleTranslator.visit_raises_field().
        for node in section.children:
            if not node.hasattr('type'):
                section['as_list'] = True
                break

    def process_warns(self, section):
        # This section contains list of fields, which contains bullet list)
        # (because napoleon docstring converts 'Warns' like that).
        #
        # Here we convert billet list items to paragraph lines and replace
        # all fields with the paragraph.
        lines = []
        for field in section.children[:]:
            section.remove(field)
            # Skip nodes with empty content.
            if not len(field[1]):
                continue
            bullet_list = field[1][0]
            if isinstance(bullet_list, nodes.bullet_list):
                for item in bullet_list:
                    # Expected structure:
                    # <list_item><paragraph><strong/></paragraph></list_item>
                    if len(item) == 1 and isinstance(item[0], nodes.paragraph):
                        if len(item[0]) == 1 and isinstance(item[0][0], nodes.strong):
                            lines.append(item[0][0].astext())
                    # On unexpected node just add it's content.
                    # In such case unexpected nodes will be placed before
                    # the paragraph with expected content.
                    # But this must not happen since napoleon always constructs
                    # bullet lists.
                    else:
                        section.extend(item.children)
            else:
                section.append(bullet_list)
        if lines:
            section.append(nodes.paragraph(text='\n'.join(lines)))

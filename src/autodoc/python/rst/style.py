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

from ...style import DocstringStyle
from ...settings import C
from .translator import DocumentToRstTranslator
from .transforms.add_fields import AddDocstringSections


class RstBaseStyle(DocstringStyle):
    settings_spec = (
        # TODO: have separate config for each admonition type.
        # TODO: add fake option to show generic name.
        # something like: rst_<name>_blank_line
        ('Put blank line between directive and first content line.',
         'admonition_blank_line', False),  # num or only bool?

        ('Extra indentation for the directive content.',
         'admonition_indent', 4),

        (
            """
            Put first content line on the same line as directive.
            None means 'auto' - put if content is one line and short.
            True - put
            False - don't put
            """,
            'admonition_on_first_line', None, (None, bool)
        ),

        (
            """
            Field body indent.
            null - indent with default indentation.
            yes - indent to field name.
            <int> - use this indentation value.
            """,
            'field_body_indent', None,
            (None, bool, int)
        ),

        ('Separate fields with blank line.', 'field_margin', False, (int, bool)),
        ('Separate options with blank line.', 'opt_margin', False),
    )


class RstStyle(RstBaseStyle):
    name = 'rst'
    settings_section = name
    settings_spec_help = 'reStructuredText docstring style.'
    settings_spec = RstBaseStyle.settings_spec + (
        (
            """
            Always have separate :type: for the :param: field.
            False means inline simple types (with no spaces) to the :param:
            and have separate :type: for the complex ones.
            """,
            'separate_param_type', False
        ),

        ('Separate field blocks (params, returns, raises) with a blank line',
         'separate_info_fields', False),

        ('Params tag', 'params_tag', 'param', C('parameter', 'param')),
        ('Returns tag', 'returns_tag', 'returns', C('return', 'returns')),
        ('Raises tag', 'raises_tag', 'raises', C('raise', 'raises')),
    )

    document_translator_cls = DocumentToRstTranslator
    transforms = (AddDocstringSections,)

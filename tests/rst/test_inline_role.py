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

from __future__ import absolute_import


# Test: inline markup roles + unknown roles.
class TestRole:
    # Test: inline markups with disabled shorten option.
    #
    # :emphasis:
    # :strong:
    # :literal:
    # :subscript:, :sub:
    # :superscript:, :sup:
    # :title-reference:, :t:, :title:
    def test_basic_inline_markup_long(self, assert_py_doc):
        assert_py_doc(
            settings=dict(shorten_inline=False, line_width=None),
            text=r"""
            Test inline markup roles.

            Long roles:
            :emphasis:`emp`, :strong:`strong`,
            :literal:`literal`, :subscript:`subscript text` OR :sub:`sub text`,
            :superscript:`superscript text` OR :sup:`sup text`,

            :title-reference:`Title reference` OR :t:`t ref`
            OR :title:`title ref`,

            :math:`A_\text{c} = (\pi/4) d^2`

            Short roles:
            Bla *emphasis*, **strong emphasis**, ``literal text``,
            `default role`.

            Special case for the literal:
            ``text \ and \\ backslashes``
            :literal:`text \ and \\ backslashes`
            """
        )

    # Test: inline markups with enabled shorten option.
    def test_basic_inline_markup_short(self, assert_py_doc):
        assert_py_doc(
            settings=dict(shorten_inline=True, line_width=None),
            text="""
            Test inline markup roles.

            Long roles:
            :emphasis:`emp`, :strong:`strong`,
            :literal:`literal`, :subscript:`subscript text` OR :sub:`sub text`,
            :superscript:`superscript text` OR :sup:`sup text`,

            :title-reference:`Title reference` OR :t:`t ref`
            OR :title:`title ref`,

            Short roles:
            Bla *emphasis*, **strong emphasis**, ``literal text``,
            `interpreted text`.
            """,
            expected="""
            Test inline markup roles.

            Long roles:
            *emp*, **strong**,
            ``literal``, :sub:`subscript text` OR :sub:`sub text`,
            :sup:`superscript text` OR :sup:`sup text`,

            :t:`Title reference` OR :t:`t ref`
            OR :t:`title ref`,

            Short roles:
            Bla *emphasis*, **strong emphasis**, ``literal text``,
            `interpreted text`.
            """
        )

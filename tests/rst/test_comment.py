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

# Test: comments.
class TestComments:
    # Test: comments.
    def test_directive_comment(self, assert_py_doc):
        assert_py_doc(
            settings=dict(line_width=None),
            text="""
            This is a paragraph.

            .. Comments begin with two dots and a space.  Anything may
               follow, except for the syntax of footnotes/citations,
               hyperlink targets, directives, or substitution definitions.
    
               Par 2 targets, directives, or substitution definitions.
        """)

    def test_directive_comment_wrap(self, assert_py_doc):
        assert_py_doc(
            settings=dict(line_width=45),
            text="""
            This is a paragraph.

            .. Comments begin with two dots and a space.  Anything may
               follow, except for the syntax of footnotes/citations,
               hyperlink targets, directives, or substitution definitions.

               Par 2 targets, directives, or substitution definitions.
            """,
            expected="""
            This is a paragraph.

            .. Comments begin with two dots and a space.
               Anything may follow, except for the syntax
               of footnotes/citations, hyperlink targets,
               directives, or substitution definitions.

               Par 2 targets, directives, or substitution
               definitions.
            """)

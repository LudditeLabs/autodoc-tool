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

# Test: sections
class TestSection:
    # Test: sections with source code lines passed.
    def test_sections_with_src(self, assert_py_doc):
        assert_py_doc(
            text="""
            ===============
             Section Title
            ===============

            text

            ----------------
             Section Title1
            ----------------

            text1

            Section Title2
            ==============

            text2

            Section Title2
            ==============

            text2.1

            Section Title3
            --------------

            Section Title4
            ``````````````

            Section Title5
            ''''''''''''''

            Section Title6
            ..............

            Section Title7
            ~~~~~~~~~~~~~~

            Section Title8
            **************

            Section Title9
            ++++++++++++++

            Section Title10
            ^^^^^^^^^^^^^^^

            Section Title11
            %%%%%%%%%%%%%%%

            Section Title12
            ]]]]]]]]]]]]]]]
            """
        )

    # Test: sections without passing src lines.
    # In this case section markers will be calculated on sections levels.
    # But there is no way to detect if overline & padding is used.
    # Also sections styles are limited and has predefined order.
    def test_sections_no_src(self, assert_py_doc):
        # Without source code lines
        assert_py_doc(
            text="""
            ===============
             Section Title
            ===============

            text

            ----------------
             Section Title1
            ----------------

            text1

            Section Title2
            ==============

            text2

            Section Title2
            ==============

            text2.1

            Section Title3
            --------------

            Section Title4
            ``````````````

            Section Title5
            ''''''''''''''

            Section Title6
            ..............

            Section Title7
            ~~~~~~~~~~~~~~

            Section Title8
            **************

            Section Title9
            ++++++++++++++

            Section Title10
            ^^^^^^^^^^^^^^^

            Section Title11
            %%%%%%%%%%%%%%%

            Section Title11
            ]]]]]]]]]]]]]]]
            """,
            expected="""
            Section Title
            =============

            text

            Section Title1
            --------------

            text1

            Section Title2
            ``````````````

            text2

            Section Title2
            ::::::::::::::

            text2.1

            Section Title3
            ..............

            Section Title4
            ''''''''''''''

            Section Title5
            \"\"\"\"\"\"\"\"\"\"\"\"\"\"

            Section Title6
            ~~~~~~~~~~~~~~

            Section Title7
            ^^^^^^^^^^^^^^

            Section Title8
            ______________

            Section Title9
            **************

            Section Title10
            +++++++++++++++

            Section Title11
            ###############

            Section Title11
            ###############
            """,
            pass_lines=False
        )

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

# Test: line block.
class TestLineBlock:
    # Test: simple line block.
    def test_simple(self, assert_py_doc):
        assert_py_doc(
            """
            Top line.

            | Lend us a couple of bob till Thursday.
            | I'm absolutely skint.
            | But I'm expecting a postal order and I can pay you back
              as soon as it comes.
            | Love, Ewan.

            Bottom line.
            """)

    # Test: line block inside a quoted block.
    def test_in_quoted_block(self, assert_py_doc):
        assert_py_doc(
            """
            Take it away, Eric the Orchestra Leader!

                | A one, two, a one two three four
                |
                |
                | Singing...

            Bottom line.
            """)

    # Test: line block with inline markup.
    # NOTE: original indentation is not supported yet.
    def test_with_inline_markup(self, assert_py_doc):
        assert_py_doc(
            text="""
            Take it away, Eric the Orchestra Leader!

                | A one, two, a one two three four
                |
                | Half a bee, philosophically,
                |     must, *ipso facto*, half not be.
                | But half the bee has got to be,
                |     *vis a vis* its entity.  D'you see?
                |
                | But can a bee be said to be
                |     or not to be an entire bee,
                |         when half the bee is not a bee,
                |             due to some ancient injury?
                |
                | Singing...

            Bottom line.
            """,
            expected="""
            Take it away, Eric the Orchestra Leader!

                | A one, two, a one two three four
                |
                | Half a bee, philosophically,
                | must, *ipso facto*, half not be.
                | But half the bee has got to be,
                | *vis a vis* its entity.  D'you see?
                |
                | But can a bee be said to be
                | or not to be an entire bee,
                | when half the bee is not a bee,
                | due to some ancient injury?
                |
                | Singing...

            Bottom line.
            """
        )

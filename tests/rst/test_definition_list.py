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

# Test: definition lists.
class TestDefinitionList:
    def test_def_list(self, assert_py_doc):
        assert_py_doc(
            text="""
            term 1
                Definition 1.

            term 2
                Definition 2, paragraph 1.

                Definition 2, paragraph 2.

            term 3 : classifier
                Definition 3.

            term 4 : classifier one : classifier two
                Definition 4.

                Bla *emphasis*, **strong emphasis**, ``literal text``,
                `interpreted text`.

                - One

                - Two
            """
        )

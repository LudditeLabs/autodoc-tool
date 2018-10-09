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

# TODO: add more tests.
# Test: convert document to text when punctuation
# and enclosing chars exists near boxed words.
class TestPunctuation:
    def test_simple(self, assert_py_doc):
        assert_py_doc(
            settings=dict(line_width=80),
            text="""
            This is a paragraph.
    
            :myrole:`ddd`.
            
            Bla (:acronym:`ddd`). But ) :func:`xxx` with space!
            
            :any:`xxx` ... some word
            
            :any:`xxx`... some word
    
            ***dssd***, ```literal text```
            
            Line of text.
            """)

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

# Test: test unknown roles and directives.
class TestUnknown:
    # Test: unknown roles.
    def test_role(self, assert_py_doc):
        # 'acronym' is known role, but not supported by the CommonTranslator
        # it will be processed by the default role handler.
        # 'myrole' is not registered and unknown.
        # 'any' is not registered but known.
        #
        # So error message will be generated only for the 'myrole'.

        env = assert_py_doc("""
        This is a paragraph.

        :myrole:`ddd`.
        
        :acronym:`ddd`.
        
        :any:`xxx`

        ***dssd***, ```literal text```
        
        Line of text.
        """)
        doc = env['definition'].doc_block.document
        msg = doc.parse_messages
        assert len(msg) == 1
        err = msg[0].children[0]
        assert err.astext().startswith('No role entry for "myrole"')

    def test_simple(self, assert_py_doc):
        assert_py_doc(
            text="""
            This is an ordinary paragraph.

            .. note:: dsds

            .. note_ex:: This is a note admonition.

               This is the second line of the first paragraph.

               Some text:

               - The note contains all indented body elements following.

               - It includes this bullet list.

            .. imaeg_ex:: picture.jpeg
               :height: 100px
               :width: 200 px
               :scale: 50 %
               :alt: alternate text
               :align: right

               A helper function that decorates a function to retain the current
               request context. This is useful when working with greenlets.

               The moment the function is decorated a copy of the request
               context is created and then pushed when the function is called.

            .. versionadded:: 0.10
            .. versionadded:: 0.12

            .. deprecated:: 3.1
               Use :func:`spam` instead.

            .. function:: foo(x)
                          foo(y, z)
               :module: some.module.name

               Return a line of text input from the user.
            """
        )

    def test_wrap(self, assert_py_doc):
        assert_py_doc(
            settings=dict(line_width=40),
            text="""
            This is an ordinary paragraph.

            .. note:: dsds

            .. note_ex:: This is a note admonition.

               This is the second line of the first paragraph.

               Some text:

               - The note contains all indented body elements
                 following.

               - It includes this bullet list.

            .. imaeg_ex:: picture.jpeg
               :height: 100px
               :width: 200 px
               :scale: 50 %
               :alt: alternate text
               :align: right

               A helper function that decorates a function to retain the current
               request context. This is useful when working with greenlets.

               The moment the function is decorated a copy of the request
               context is created and then pushed when the function is called.

            .. versionadded:: 0.10

            .. deprecated:: 3.1
               Use :func:`spam` instead.
            """,
            expected="""
            This is an ordinary paragraph.

            .. note:: dsds

            .. note_ex:: This is a note admonition.

               This is the second line of the first
               paragraph.

               Some text:

               - The note contains all indented body
                 elements following.

               - It includes this bullet list.

            .. imaeg_ex:: picture.jpeg
               :height: 100px
               :width: 200 px
               :scale: 50 %
               :alt: alternate text
               :align: right

               A helper function that decorates a
               function to retain the current
               request context. This is useful when
               working with greenlets.

               The moment the function is decorated
               a copy of the request context is
               created and then pushed when the
               function is called.

            .. versionadded:: 0.10

            .. deprecated:: 3.1
               Use :func:`spam` instead.
            """
        )

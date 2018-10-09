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

from autodoc.contentdb import Arg

docstring_style = 'rst'
docstring_keep_transforms = True


# TODO: add more tests.
# Test: convert python docstring to plan reStructuredText.
class TestStyleRst:
    # Test: complex docstring.
    def test_complex(self, assert_py_doc):
        args = (Arg('sender', ['str']),
                Arg('recipient', ['str']),
                    Arg('message_body', ['str']),
                Arg('priority', ['integer', 'float']))

        assert_py_doc(
            args=args,
            text="""
            This is an ordinary paragraph.
    
            >>> print 'this is a Doctest block'
            this is a Doctest block
    
            The following is a literal block::
    
                >>> This is not recognized as a doctest block by
                reStructuredText.  It *will* be recognized by the doctest
                module, though!
    
            .. versionadded:: 0.10
    
            Bottom line.
    
            :parameter:
            :param str sender: The person sending the message
            :param str message_body: The body of the message
            :param str recipient: NOTE! THIS PARAM MUST BE PLACED AFTER sender!
            :parameter priority: The priority of the message,
                can be a number 1-5
            :type priority: integer or float
            :return bla bla: Hz
            :return: the message id
            :rtype: int
            :return: the message id2
            :rtype: char
            :rtype: string
            :raises ValueError: if the message_body exceeds 160 characters
            :raises TypeError: if the message_body is not a basestring
    
            .. seealso:: Another function.
            .. note:: Lorem ipsum dolor sit amet, consectetur adipiscing elit.
            
            :Yields: eos qui ratione voluptatem sequi nesciunt.
                Neque porro quisquam est, qui dolorem ipsum quia dolor sit amet
            """,
            expected="""
            This is an ordinary paragraph.
    
            >>> print 'this is a Doctest block'
            this is a Doctest block
    
            The following is a literal block::
    
                >>> This is not recognized as a doctest block by
                reStructuredText.  It *will* be recognized by the doctest
                module, though!
    
            .. versionadded:: 0.10
    
            Bottom line.
    
            :param str sender: The person sending the message
            :param str recipient: NOTE! THIS PARAM MUST BE PLACED AFTER sender!
            :param str message_body: The body of the message
            :param priority: The priority of the message, can be a number 1-5
            :type priority: integer or float
            :returns: the message id
            :rtype: int
            :returns: the message id2
            :rtype: char
            :rtype: string
            :raises ValueError: if the message_body exceeds 160 characters
            :raises TypeError: if the message_body is not a basestring
            :Yields: eos qui ratione voluptatem sequi nesciunt. Neque porro
                quisquam est, qui dolorem ipsum quia dolor sit amet

            .. seealso:: Another function.

            .. note:: Lorem ipsum dolor sit amet, consectetur adipiscing elit.
            """
        )

    # Test: add missing params.
    def test_missing_params(self, assert_py_doc):
        args = (Arg('sender', ['str']),
                Arg('recipient', ['str']),
                Arg('message_body', ['str']))

        assert_py_doc(
            args=args,
            text="""
            This is an ordinary paragraph.

            >>> print 'this is a Doctest block'
            this is a Doctest block

            The following is a literal block::

                >>> This is not recognized as a doctest block by
                reStructuredText.  It *will* be recognized by the doctest
                module, though!

            .. versionadded:: 0.10

            Bottom line.

            .. seealso:: Another function.
            .. note:: Lorem ipsum dolor sit amet, consectetur adipiscing elit.
            """,
            expected="""
            This is an ordinary paragraph.

            >>> print 'this is a Doctest block'
            this is a Doctest block

            The following is a literal block::

                >>> This is not recognized as a doctest block by
                reStructuredText.  It *will* be recognized by the doctest
                module, though!

            .. versionadded:: 0.10

            Bottom line.

            .. seealso:: Another function.
            
            .. note:: Lorem ipsum dolor sit amet, consectetur adipiscing elit.

            :param str sender:
            :param str recipient:
            :param str message_body:
            """
        )

    # Test: keyword field.
    def test_keyword(self, assert_py_doc):
        assert_py_doc(
            text="""
            This is an ordinary paragraph.

            :keyword name: Same as examples section.
                           Quis autem vel eum iure reprehenderit qui
                           Examples should be written in doctest format,
                           illustrate how to use the function.
            :kwtype name: str, sds
            
            :keyword one: Examples should be written in doctest format
            :kwtype one: int

            Bottom line.
            """,
            expected="""
            This is an ordinary paragraph.

            :keyword name: Same as examples section. Quis autem vel eum iure
                reprehenderit qui Examples should be written in doctest format,
                illustrate how to use the function.
            :kwtype name: str, sds
            :keyword int one: Examples should be written in doctest format

            Bottom line.
            """
        )

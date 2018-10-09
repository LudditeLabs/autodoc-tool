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

# Test: doctest block.
class TestDoctest:
    def test_simple(self, assert_py_doc):
        assert_py_doc(
            """
            This is an ordinary paragraph.

            >>> print 'this is a Doctest block'
            this is a Doctest block

            The following is a literal block::

                >>> This is not recognized as a doctest block by
                reStructuredText.  It *will* be recognized by the doctest
                module, though!

            Bottom line.
            """)

    # NOTE: This construction (without blank lines) causes errors:
    # Traceback (most recent call last):
    #    ...
    # ValueError: n must be >= 0
    #
    # It thinks what '...' is a block quote.
    # As a result it will have top and bottom blank lines.
    def test_complex(self, assert_py_doc):
        assert_py_doc(
            text="""
            Return the factorial of n, an exact integer >= 0.

            If the result is small enough to fit in an int, return an int. Else
            return a long.

            >>> [factorial(n) for n in range(6)]
            [1, 1, 2, 6, 24, 120]
            >>> [factorial(long(n)) for n in range(6)]
            [1, 1, 2, 6, 24, 120]
            >>> factorial(30)
            265252859812191058636308480000000L
            >>> factorial(30L)
            265252859812191058636308480000000L
            >>> factorial(-1)
            Traceback (most recent call last):
            ...
            ValueError: n must be >= 0

            Factorials of floats are OK, but the float must be an exact integer:
            
            >>> factorial(30.1)
            Traceback (most recent call last):
            ...
            ValueError: n must be exact integer
            >>> factorial(30.0)
            265252859812191058636308480000000L

            It must also not be ridiculously large:
            
            >>> factorial(1e100)
            Traceback (most recent call last):
            ...
            OverflowError: n too large
            """
        )

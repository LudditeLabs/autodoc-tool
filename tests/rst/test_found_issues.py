"""
Tests for found issues.
Some of them are marked as failed because not fixed yet.
"""
import pytest


class TestIssues:
    # Test: List is not detected by parser since the list if not separated with
    # blank line.
    @pytest.mark.xfail(strict=True, raises=AssertionError, reason='Improve me')
    def test_incorrect_list(self, assert_py_doc):
        assert_py_doc("""
        checks for sign of poor/misdesign:
        * number of methods, attributes, local variables...
        * size, complexity of functions, methods
        """)

    # Test: wrap when a link (boxed word) following a punctuation char.
    # Make sure the link is separated from the punctuation.
    def test_boxed_after_punctuation(self, assert_py_doc):
        assert_py_doc(
            text="""
            Code extracted from 'pytest/setup.py'
            https://github.com/pytest-dev/pytest/blob/7538680c/setup.py#L31
            The first known release to support environment marker with range operators
            it is 17.1, see: https://setuptools.readthedocs.io/en/latest/history.html#id113
            """,
            expected="""
            Code extracted from 'pytest/setup.py'
            https://github.com/pytest-dev/pytest/blob/7538680c/setup.py#L31 The     
            first known release to support environment marker with range
            operators it is 17.1, see:
            https://setuptools.readthedocs.io/en/latest/history.html#id113
            """)

    # Test: bug: extra space after nid
    def test_dot_after_boxed(self, assert_py_doc):
        assert_py_doc("""Returns a suitable DOT node id for `nid`.""")

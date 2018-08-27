from autodoc.utils import trim_docstring, get_indent, get_line_indent


# Test: trim_docstring().
class TestTrimDocstring:
    # Test: empty content.
    def test_empty(self):
        lines = trim_docstring("""

        """)
        assert lines == ['', '', '']

        lines = trim_docstring('')
        assert lines == ['']

    # Test: common case - first line has content.
    def test_first_nonempty(self):
        lines = trim_docstring("""Bla bla.

            More bla bla.

            :param a: First parameter.
            :param b: Second parameter.
            :return:  Sum
        """)

        lst = ['Bla bla.', '',
               'More bla bla.',
               '',
               ':param a: First parameter.',
               ':param b: Second parameter.',
               ':return:  Sum',
               '']
        assert lst == lines

    # Test: don't remove first empty line, correct indentation.
    def test_first_empty(self):
        lines = trim_docstring("""
        More bla bla.

            First parameter.
                Second parameter.
        Sum
        """)

        lst = ['',
               'More bla bla.',
               '',
               '    First parameter.',
               '        Second parameter.',
               'Sum',
               '']
        assert lst == lines

    # Test: strip off leading blank lines.
    def test_strip_leading(self):
        lines = trim_docstring("""

        More bla bla.

            First parameter.
                Second parameter.
        Sum
        """, strip_leading=True)

        lst = ['More bla bla.',
               '',
               '    First parameter.',
               '        Second parameter.',
               'Sum',
               '']
        assert lst == lines

    # Test: strip off trailing blank lines.
    def test_strip_trailing(self):
        lines = trim_docstring("""
        More bla bla.

            First parameter.
                Second parameter.
        Sum


        """, strip_trailing=True)

        lst = ['',
               'More bla bla.',
               '',
               '    First parameter.',
               '        Second parameter.',
               'Sum']
        assert lst == lines

    # Test: strip off trailing blank lines.
    def test_strip_all(self):
        lines = trim_docstring("""


        More bla bla.

            First parameter.
                Second parameter.
        Sum


        """, strip_leading=True, strip_trailing=True)

        lst = ['More bla bla.',
               '',
               '    First parameter.',
               '        Second parameter.',
               'Sum']
        assert lst == lines

    # Test: strip trailing/leading and return string instead of lines.
    def test_as_string(self):
        lines = trim_docstring("""
        More bla bla.

            First parameter.
                Second parameter.
        Sum
        """, strip_leading=True, strip_trailing=True, as_string=True)

        lst = ['More bla bla.',
               '',
               '    First parameter.',
               '        Second parameter.',
               'Sum']
        assert '\n'.join(lst) == lines

    # Test: pass list as input.
    def test_list(self):
        lines = trim_docstring([''
            '    More bla bla.',
            '       ',
            '        First parameter.',
            '            Second parameter.',
            '    Sum'],
            strip_leading=True, strip_trailing=True, as_string=False)

        lst = ['More bla bla.',
               '',
               '    First parameter.',
               '        Second parameter.',
               'Sum']
        assert lines == lst


# Test: indentation functions.
class TestIndent:
    # Test: get_indent() function.
    def test_get_indent(self):
        assert get_indent('hello') == 0
        assert get_indent(' hello') == 1
        assert get_indent('   h e l l o   ') == 3

        # Input text must be tab expanded, otherwise indent will be incorrect.
        assert get_indent('\thello') == 1

    # Test: get_line_indent() function.
    def test_get_line_indent(self):
        lines = [
            'def find(pattern, path):',                         # 0
            '    result = []',                                  # 1
            '    for root, dirs, files in os.walk(path):',
            '    ',                                             # 3
            '      ',
            '        for name in files:',                       # 5
            '            if fnmatch.fnmatch(name, pattern):',
            '                result.append(os.path.join(root, name))',
            '    return result',
            '    ',                                             # 9
        ]

        assert get_line_indent(lines, 0) == 0
        assert get_line_indent(lines, 1) == 4

        # In this situation we skip all blank lines and stop at pos 5.
        assert get_line_indent(lines, 3) == 8

        # Here None is returned since we reached end of lines.
        assert get_line_indent(lines, 9) is None

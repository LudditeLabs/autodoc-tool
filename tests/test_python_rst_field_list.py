# TODO: list in a field body doesn't work
# See http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html#field-lists
#
# Input:
#
#     :Authors: - Me
#               - Myself
#               - I
#
# Output :
#
#     :Authors:
#       - Me
#       - Myself
#       - I
#


# Test: field lists.
class TestRstFieldList:
    def test_simple(self, assert_py_doc):
        assert_py_doc(
            text="""
            Top text.

            :Indentation: Since the field marker may be quite long, the second
                and subsequent lines of the field body do not have to line up

                with the first line, but they must be indented relative to the
                field name marker, and they must line up with each other.
            :Parameter i: integer
            :Date: 2001-08-16
            :Version: 1
            :empty param:
            :Authors:
                - Me
                - Myself
                - I
            :VersionX:

            Bottom text.
            """
        )

    # Test: indentation values.
    def test_indent(self, assert_py_doc):
        # Indent to the field name
        settings = dict(field_body_indent=True)

        assert_py_doc(
            settings=settings,
            text="""
            Top text.

            :Parameter i: integer
            :Date: 2001-08-16
            :Version: 1
            :Indentation: Since the field marker may be quite long, the second
                and subsequent lines of the field body do not have to ...

            Bottom text.
            """,
            expected="""
            Top text.

            :Parameter i: integer
            :Date: 2001-08-16
            :Version: 1
            :Indentation: Since the field marker may be quite long, the second
                          and subsequent lines of the field body do not have to
                          ...

            Bottom text.
            """
        )

        # Indent with one space
        settings['field_body_indent'] = 1

        assert_py_doc(
            settings=settings,
            text="""
            Top text.

            :Parameter i: integer
            :Date: 2001-08-16
            :Version: 1
            :Indentation: Since the field marker may be quite long, the second
                and subsequent lines of the field body do not have to ...

            Bottom text.
            """,
            expected="""
            Top text.

            :Parameter i: integer
            :Date: 2001-08-16
            :Version: 1
            :Indentation: Since the field marker may be quite long, the second
             and subsequent lines of the field body do not have to ...

            Bottom text.
            """
        )

        # Indent with default indent.
        settings['field_body_indent'] = None
        settings['indent'] = 6

        assert_py_doc(
            settings=settings,
            text="""
            Top text.

            :Parameter i: integer
            :Date: 2001-08-16
            :Version: 1
            :Indentation: Since the field marker may be quite long, the second
                and subsequent lines of the field body do not have to ...
            :VersionX:

            Bottom text.
            """,
            expected="""
            Top text.

            :Parameter i: integer
            :Date: 2001-08-16
            :Version: 1
            :Indentation: Since the field marker may be quite long, the second
                  and subsequent lines of the field body do not have to ...
            :VersionX:

            Bottom text.
            """
        )

    def test_wrap(self, assert_py_doc):
        assert_py_doc(
            settings=dict(line_width=40),
            text="""
            Top text.

            :Indentation: Since the field marker may be quite long, the second
                      and subsequent lines of the field body do not have to ...
            :VersionX:
            :Parameter i: integer
            :Date: 2001-08-16
            :Version: 1
            :VersionX:

            Bottom text.
            """,
            expected="""
            Top text.

            :Indentation: Since the field marker may
                be quite long, the second and
                subsequent lines of the field body
                do not have to ...
            :VersionX:
            :Parameter i: integer
            :Date: 2001-08-16
            :Version: 1
            :VersionX:

            Bottom text.
            """
        )

    # Test: blank lines between fields.
    def test_margin(self, assert_py_doc):
        assert_py_doc(
            settings=dict(field_margin=True, line_width=66),
            text="""
            Top text.

            :Parameter i: integer
            :Date: 2001-08-16
            :Version: 1
            :Indentation: Since the field marker may be quite long, the second
                and subsequent lines of the field body do not have to ...

            Bottom text.
            """,
            expected="""
            Top text.

            :Parameter i: integer

            :Date: 2001-08-16

            :Version: 1

            :Indentation: Since the field marker may be quite long, the second
                and subsequent lines of the field body do not have to ...

            Bottom text.
            """
        )

        assert_py_doc(
            settings=dict(field_margin=2, line_width=66),
            text="""
            Top text.

            :Parameter i: integer
            :Date: 2001-08-16
            :Version: 1
            :Indentation: Since the field marker may be quite long, the second
                and subsequent lines of the field body do not have to ...

            Bottom text.
            """,
            expected="""
            Top text.

            :Parameter i: integer


            :Date: 2001-08-16


            :Version: 1


            :Indentation: Since the field marker may be quite long, the second
                and subsequent lines of the field body do not have to ...

            Bottom text.
            """
        )

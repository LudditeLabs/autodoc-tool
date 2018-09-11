# Test: comments.
class TestComments:
    # Test: comments.
    def test_directive_comment(self, assert_py_doc):
        assert_py_doc(
            settings=dict(line_width=None),
            text="""
            This is a paragraph.

            .. Comments begin with two dots and a space.  Anything may
               follow, except for the syntax of footnotes/citations,
               hyperlink targets, directives, or substitution definitions.
    
               Par 2 targets, directives, or substitution definitions.
        """)

    def test_directive_comment_wrap(self, assert_py_doc):
        assert_py_doc(
            settings=dict(line_width=45),
            text="""
            This is a paragraph.

            .. Comments begin with two dots and a space.  Anything may
               follow, except for the syntax of footnotes/citations,
               hyperlink targets, directives, or substitution definitions.

               Par 2 targets, directives, or substitution definitions.
            """,
            expected="""
            This is a paragraph.

            .. Comments begin with two dots and a space.
               Anything may follow, except for the syntax
               of footnotes/citations, hyperlink targets,
               directives, or substitution definitions.

               Par 2 targets, directives, or substitution
               definitions.
            """)

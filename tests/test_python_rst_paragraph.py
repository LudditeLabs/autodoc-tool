# Test: paragraphs and block quotes.
class TestRstParagraphAndBq:
    # Test: common paragraphs and block quotes.
    # NOTE: currently multiple blank lines are ignored.
    def test_paragraph(self, assert_py_doc):
        assert_py_doc(
            settings=dict(line_width=None),
            text="""
            This is a paragraph.  It's quite
            short.

                This paragraph will result in an indented block of
                text, typically used for quoting other text.

            This is a top-level paragraph.

                This paragraph belongs to a first-level block quote.

                    This paragraph belongs to a second-level block quote.

            Another top-level paragraph.

                    Bellow multiple blank lines will be ignored.



                This paragraph belongs to a first-level block quote.  The
                second-level block quote above is inside this first-level
                block quote.
            """,
            expected="""
            This is a paragraph.  It's quite
            short.

                This paragraph will result in an indented block of
                text, typically used for quoting other text.

            This is a top-level paragraph.

                This paragraph belongs to a first-level block quote.

                    This paragraph belongs to a second-level block quote.

            Another top-level paragraph.

                    Bellow multiple blank lines will be ignored.

                This paragraph belongs to a first-level block quote.  The
                second-level block quote above is inside this first-level
                block quote.
            """,
            pass_lines=False
        )

    # Test: paragraph and block quotes wrapping.
    def test_paragraph_wrap(self, assert_py_doc):
        assert_py_doc(
            settings=dict(line_width=45),
            text="""
            This is a paragraph.  It's quite
            short.

                This paragraph will result in an indented block of
                text, typically used for quoting other text.

            This is a top-level paragraph.

                This paragraph belongs to a first-level block quote.

                    This paragraph belongs to a second-level block quote.

            Another top-level paragraph.

                    Bellow multiple blank lines will be ignored.



                This paragraph belongs to a first-level block quote.  The
                second-level block quote above is inside this first-level
                block quote.
            """,
            expected="""
            This is a paragraph. It's quite short.

                This paragraph will result in an indented
                block of text, typically used for quoting
                other text.

            This is a top-level paragraph.

                This paragraph belongs to a first-level
                block quote.

                    This paragraph belongs to a
                    second-level block quote.

            Another top-level paragraph.

                    Bellow multiple blank lines will be
                    ignored.

                This paragraph belongs to a first-level
                block quote. The second-level block quote
                above is inside this first-level block
                quote.
            """,
            pass_lines=False
        )

    # Test: block quote attribution.
    def test_block_quote_attribution(self, assert_py_doc):
        assert_py_doc(
            text="""
            This is an ordinary paragraph, introducing a block quote.

                "It is my business to know things. That is my trade."

                -- Sherlock Holmes
            """
        )

    # Test: block quote variants.
    def test_block_quote(self, assert_py_doc):
        assert_py_doc(
            text="""
            Multiple block quotes may occur consecutively if terminated with
            attributions.

                Unindented paragraph.

                    Block quote 1.

                    -- Attribution 1

                    Block quote 2.

            Empty comments may be used to explicitly terminate preceding
            constructs that would otherwise consume a block quote:

            * List item.

            ..

                Block quote 3.

            Empty comments may also be used to separate block quotes:

                Block quote 4.

            ..

                Block quote 5.

            Blank lines are required before and after a block quote, but these
            blank lines are not included as part of the block quote.
            """
        )

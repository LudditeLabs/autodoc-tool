# Test: line block.
class TestLineBlock:
    # Test: simple line block.
    def test_simple(self, assert_py_doc):
        assert_py_doc(
            """
            Top line.

            | Lend us a couple of bob till Thursday.
            | I'm absolutely skint.
            | But I'm expecting a postal order and I can pay you back
              as soon as it comes.
            | Love, Ewan.

            Bottom line.
            """)

    # Test: line block inside a quoted block.
    def test_in_quoted_block(self, assert_py_doc):
        assert_py_doc(
            """
            Take it away, Eric the Orchestra Leader!

                | A one, two, a one two three four
                |
                |
                | Singing...

            Bottom line.
            """)

    # Test: line block with inline markup.
    # NOTE: original indentation is not supported yet.
    def test_with_inline_markup(self, assert_py_doc):
        assert_py_doc(
            text="""
            Take it away, Eric the Orchestra Leader!

                | A one, two, a one two three four
                |
                | Half a bee, philosophically,
                |     must, *ipso facto*, half not be.
                | But half the bee has got to be,
                |     *vis a vis* its entity.  D'you see?
                |
                | But can a bee be said to be
                |     or not to be an entire bee,
                |         when half the bee is not a bee,
                |             due to some ancient injury?
                |
                | Singing...

            Bottom line.
            """,
            expected="""
            Take it away, Eric the Orchestra Leader!

                | A one, two, a one two three four
                |
                | Half a bee, philosophically,
                | must, *ipso facto*, half not be.
                | But half the bee has got to be,
                | *vis a vis* its entity.  D'you see?
                |
                | But can a bee be said to be
                | or not to be an entire bee,
                | when half the bee is not a bee,
                | due to some ancient injury?
                |
                | Singing...

            Bottom line.
            """
        )

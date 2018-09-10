# Test: bullet and enumerated lists.
class TestRstList:
    # Test: test bullet lists
    # A text block which begins with a "*", "+", "-".
    # followed by whitespace, is a bullet list item
    # (a.k.a. "unordered" list item). List item bodies must be left-aligned
    # and indented relative to the bullet; the text immediately after the
    # bullet determines the indentation.
    def test_list_bullet_with_src(self, assert_py_doc):
        assert_py_doc(
            text="""
            - This is the first bullet list item. The blank line above the first
              list item is required; blank lines between list items

              (such as below this paragraph) are optional.
            - This is the first paragraph in the second item in the list.

              This is the second paragraph in the second item in the list. The
              blank line above this paragraph is required. The left edge of this
              paragraph lines up with the paragraph above, both indented
              relative to the bullet.

              * This is a sublist. The bullet lines up with the left edge of the
                text blocks above. A sublist is a new list so requires a blank
                line above and below.

            - This is the third item of the main list.

            This paragraph is not part of the list.

            + One
            
              Two
              
            + Three
            """
        )

    # Test: same as before, but without passing sources.
    def test_list_bullet_no_src(self, assert_py_doc):
        assert_py_doc(
            text="""
            - This is the first bullet list item. The blank line above the first
              list item is required; blank lines between list items (such as
              below this paragraph) are optional.
            - This is the first paragraph in the second item in the list.

              This is the second paragraph in the second item in the list.
              The blank line above this paragraph is required.  The left edge
              of this paragraph lines up with the paragraph above, both
              indented relative to the bullet.

              * This is a sublist.  The bullet lines up with the left edge of
                the text blocks above.  A sublist is a new list so requires a
                blank line above and below.

            - This is the third item of the main list.

            This paragraph is not part of the list.

            + One
              Two
            + Three
            """,
            expected="""
            - This is the first bullet list item. The blank line above the first
              list item is required; blank lines between list items (such as
              below this paragraph) are optional.

            - This is the first paragraph in the second item in the list.

              This is the second paragraph in the second item in the list. The
              blank line above this paragraph is required. The left edge of this
              paragraph lines up with the paragraph above, both indented
              relative to the bullet.

              * This is a sublist. The bullet lines up with the left edge of the
                text blocks above. A sublist is a new list so requires a blank
                line above and below.

            - This is the third item of the main list.

            This paragraph is not part of the list.

            + One Two

            + Three
            """,
            pass_lines=False
        )

    # Test: test bullet lists
    # A text block which begins with a "*", "+", "-".
    # followed by whitespace, is a bullet list item
    # (a.k.a. "unordered" list item). List item bodies must be left-aligned
    # and indented relative to the bullet; the text immediately after the
    # bullet determines the indentation.
    def test_list_enum_with_src(self, assert_py_doc):
        assert_py_doc(
            text="""
            This paragraph is not part of the list.

            1. a) Item 1a. Item 1a2.
               b) Item 1b.

            2. Item 2 initial text.

               a) Item 2a.
               b) Item 2b.

            3. (a) Item 3a.
               (b) Item 3b.

            4. (A) Item 4a.
               (B) Item 4b.

            5. (I) Item 5a.
               (II) Item 5b.

            i. Item 4a.
            
               Txt
               
            i. Item 4b. Txt
            """
        )
        assert_py_doc(
            text="""
            This paragraph is not part of the list.

            1. a) Item 1a.
               b) Item 1b.

            2. Item 2 initial text.

               a) Item 2a.
               b) Item 2b.

            3. (a) Item 3a.
               (b) Item 3b.

            4. (A) Item 4a.
               (B) Item 4b.

            5. (I) Item 5a.
               (II) Item 5b.

            #. Auto enum1.

            i. Item 4a.
            #. Item 4b.
            #. auto enum2
            """,
            expected="""
            This paragraph is not part of the list.

            1. a) Item 1a.
               b) Item 1b.

            2. Item 2 initial text.

               a) Item 2a.
               b) Item 2b.

            3. (a) Item 3a.
               (b) Item 3b.

            4. (A) Item 4a.
               (B) Item 4b.

            5. (I) Item 5a.
               (II) Item 5b.

            6. Auto enum1.

            i. Item 4a.
            ii. Item 4b.
            iii. auto enum2
            """,
        )

    def test_list_enum_no_src(self, assert_py_doc):
        assert_py_doc(
            text="""
            This paragraph is not part of the list.

            1. a) Item 1a.
               b) Item 1b.

            2. Item 2 initial text.

               a) Item 2a.
               b) Item 2b.

            3. (a) Item 3a.
               (b) Item 3b.

            4. (A) Item 4a.
               (B) Item 4b.

            5. (I) Item 5a.
               (II) Item 5b.

            #. Auto enum1.

            i. Item 4a.
            #. Item 4b.
            #. auto enum2
            """,
            expected="""
            This paragraph is not part of the list.

            1. a) Item 1a.

               b) Item 1b.

            2. Item 2 initial text.

               a) Item 2a.

               b) Item 2b.

            3. (a) Item 3a.

               (b) Item 3b.

            4. (A) Item 4a.

               (B) Item 4b.

            5. (I) Item 5a.

               (II) Item 5b.

            6. Auto enum1.

            i. Item 4a.

            ii. Item 4b.

            iii. auto enum2
            """,
            pass_lines=False
        )

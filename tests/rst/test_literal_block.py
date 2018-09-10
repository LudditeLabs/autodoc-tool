# Test: literal block.
class TestRstLiteralBlockList:
    # Test: literal block without info about source lines.
    # It must add '::' on new line if last text doesn't end with ':'
    def test_no_src(self, assert_py_doc):
        assert_py_doc(
            text="""
            This is a typical paragraph.  An indented literal block follows.
            Expanded form:

            ::

                for a in [5,4,3,2,1]:   # this is program code, shown as-is
                    print a
                print "it's..."
                # a literal block continues until the indentation ends

                one += more + line

            This text has returned to the indentation of the first paragraph,
            is outside of the literal block, and is therefore treated as an
            ordinary paragraph.

            Partially minimized form: ::

                Literal block

            Fully minimized form::

                Literal block
            """,
            expected="""
            This is a typical paragraph. An indented literal block follows.
            Expanded form::

                for a in [5,4,3,2,1]:   # this is program code, shown as-is
                    print a
                print "it's..."
                # a literal block continues until the indentation ends

                one += more + line

            This text has returned to the indentation of the first paragraph, is
            outside of the literal block, and is therefore treated as an
            ordinary paragraph.

            Partially minimized form::

                Literal block

            Fully minimized form::

                Literal block
            """,
            pass_lines=False
        )

    # Test: pass source lines. '::' line will be preserved as in original text.
    def test_src(self, assert_py_doc):
        assert_py_doc(
            text="""
            This is a typical paragraph.  An indented literal block follows.
            Expanded form:

            ::

                for a in [5,4,3,2,1]:   # this is program code, shown as-is
                    print a
                print "it's..."
                # a literal block continues until the indentation ends

                one += more + line

            This text has returned to the indentation of the first paragraph,
            is outside of the literal block, and is therefore treated as an
            ordinary paragraph.

            Partially minimized form: ::

                Literal block

            Fully minimized form::

                Literal block
            """,
            expected="""
            This is a typical paragraph. An indented literal block follows.
            Expanded form:

            ::

                for a in [5,4,3,2,1]:   # this is program code, shown as-is
                    print a
                print "it's..."
                # a literal block continues until the indentation ends

                one += more + line

            This text has returned to the indentation of the first paragraph, is
            outside of the literal block, and is therefore treated as an
            ordinary paragraph.

            Partially minimized form::

                Literal block

            Fully minimized form::

                Literal block
            """
        )

    # Test: literal block can't be wrapped.
    def test_width(self, assert_py_doc):
        assert_py_doc(
            settings=dict(line_width=50),
            text="""
            This is a typical paragraph. An indented literal
            block follows. Expanded form::

                for a in [5,4,3,2,1]:   # this is program code, shown as-is
                    print a
                print "it's..."
                # a literal block continues until the indentation ends

                one += more + line

            This text has returned to the indentation of the
            first paragraph, is outside of the literal block,
            and is therefore treated as an ordinary paragraph.

            Partially minimized form::

                Literal block

            Fully minimized form::

                Literal block
            """
        )

    # Test: literal block with quoting.
    def test_quoting(self, assert_py_doc):
        # Note what even indented block will be treated as quoted block
        # if we don't provide source code lines.
        # This is because docutils document node has no info about indentation.
        assert_py_doc(
            text="""
            This is a typical paragraph. An indented literal
            block follows. Expanded form::

            !! Great idea!
            !
            ! Why didn't I think of that?

            This text has returned to the indentation of the
            first paragraph, is outside of the literal block,
            and is therefore treated as an ordinary paragraph.

            One more::

                !! Great idea!
                ! Why didn't I think of that?
            """,
            expected="""
            This is a typical paragraph. An indented literal block follows.
            Expanded form::

            !! Great idea!
            !
            ! Why didn't I think of that?

            This text has returned to the indentation of the first paragraph, is
            outside of the literal block, and is therefore treated as an
            ordinary paragraph.

            One more::

            !! Great idea!
            ! Why didn't I think of that?
            """,
            pass_lines=False
        )

    # Test: literal block with quoting and passing src lines.
    def test_quoting_src(self, assert_py_doc):
        assert_py_doc(
            text="""
            This is a typical paragraph. An indented literal block follows.
            Expanded form::

            !! Great idea!
            !
            ! Why didn't I think of that?

            This text has returned to the indentation of the first paragraph, is
            outside of the literal block, and is therefore treated as an
            ordinary paragraph.

            One more::

                !! Great idea!
                ! Why didn't I think of that?
            """
        )

# Test: options list.
class TesOptList:
    # Test: if we don't pass source lines info and width.
    # * Left side option width must be 15
    # * Options with long descriptions have 1 blank line margin
    # * Long options have 1 blank line margin and description on next line.
    # * Other options have no margins.
    def test_no_src(self, assert_py_doc):
        assert_py_doc(
            settings=dict(line_width=None),
            text="""
            Top text.

            -a, --ax   Output all.
            -b         Output both (this description is
                       quite long).
            -c arg     Output just arg.
            --long     Output all day long.

            -p         This option has two paragraphs in the description.
                       This is the first.

                       This is the second.  Blank lines may be omitted between
                       options (as above) or left in (as here and below).

            --very-long-option  A VMS-style option.  Note the adjustment for
                                the required two spaces.

            --an-even-longer-option
                       The description can also start on the next line.

            -2, --two  This option has two variants.

            -f FILE, --file=FILE  These two options are synonyms; both have
                                  arguments.

            /V         A VMS/DOS-style option.

            Bottom text.
            """,
            expected="""
            Top text.

            -a, --ax       Output all.
            -b             Output both (this description is
                           quite long).
            -c arg         Output just arg.
            --long         Output all day long.

            -p             This option has two paragraphs in the description.
                           This is the first.

                           This is the second.  Blank lines may be omitted between
                           options (as above) or left in (as here and below).

            --very-long-option
                           A VMS-style option.  Note the adjustment for
                           the required two spaces.

            --an-even-longer-option
                           The description can also start on the next line.

            -2, --two      This option has two variants.

            -f FILE, --file=FILE
                           These two options are synonyms; both have
                           arguments.

            /V             A VMS/DOS-style option.

            Bottom text.
            """,
            pass_lines=False
        )

    # Test: if we pass no source lines info but set width.
    # * Left side option width must be width / 4
    # * Options with long descriptions have 1 blank line margin
    # * Long options have 1 blank line margin and description on next line.
    # * Other options have no margins.
    def test_no_src_width(self, assert_py_doc):
        assert_py_doc(
            settings=dict(line_width=66),
            text="""
            Top text.

            -a, --ax   Output all.
            -b         Output both (this description is
                       quite long).
            -c arg     Output just arg.
            --long     Output all day long.

            -p         This option has two paragraphs in the description.
                       This is the first.

                       This is the second.  Blank lines may be omitted between
                       options (as above) or left in (as here and below).

            --very-long-option  A VMS-style option.  Note the adjustment for
                                the required two spaces.

            --an-even-longer-option
                       The description can also start on the next line.

            -2, --two  This option has two variants.

            -f FILE, --file=FILE  These two options are synonyms; both have
                                  arguments.

            /V         A VMS/DOS-style option.

            Bottom text.
            """,
            expected="""
            Top text.

            -a, --ax        Output all.
            -b              Output both (this description is quite long).
            -c arg          Output just arg.
            --long          Output all day long.

            -p              This option has two paragraphs in the description.
                            This is the first.

                            This is the second. Blank lines may be omitted
                            between options (as above) or left in (as here and
                            below).

            --very-long-option
                            A VMS-style option. Note the adjustment for the
                            required two spaces.

            --an-even-longer-option
                            The description can also start on the next line.

            -2, --two       This option has two variants.

            -f FILE, --file=FILE
                            These two options are synonyms; both have
                            arguments.

            /V              A VMS/DOS-style option.

            Bottom text.
            """,
            pass_lines=False
        )

    # Test: if we pass source lines info but no width.
    # * Left side option width must be the same as in orig text.
    # * Options with long descriptions have 1 blank line margin
    # * Long options have 1 blank line margin and description on next line.
    # * Other options have no margins.
    def test_src(self, assert_py_doc):
        assert_py_doc(
            text="""
            Top text.

            -a, --ax   Output all.
            -b         Output both (this description is
                       quite long).
            -c arg     Output just arg.
            --long     Output all day long.

            -p         This option has two paragraphs in the description.
                       This is the first.

                       This is the second.  Blank lines may be omitted between
                       options (as above) or left in (as here and below).

            --very-long-option  A VMS-style option.  Note the adjustment for
                                the required two spaces.

            --an-even-longer-option
                       The description can also start on the next line.

            -2, --two  This option has two variants.

            -f FILE, --file=FILE  These two options are synonyms; both have
                                  arguments.

            /V         A VMS/DOS-style option.

            Bottom text.
            """,
            expected="""
            Top text.

            -a, --ax   Output all.
            -b         Output both (this description is quite long).
            -c arg     Output just arg.
            --long     Output all day long.

            -p         This option has two paragraphs in the description. This
                       is the first.

                       This is the second. Blank lines may be omitted between
                       options (as above) or left in (as here and below).

            --very-long-option
                       A VMS-style option. Note the adjustment for the required
                       two spaces.

            --an-even-longer-option
                       The description can also start on the next line.

            -2, --two  This option has two variants.

            -f FILE, --file=FILE
                       These two options are synonyms; both have arguments.

            /V         A VMS/DOS-style option.

            Bottom text.
            """,
            pass_lines=True
        )

    # Test: if we pass source lines info and width.
    # * Left side option width must be the same as in orig text.
    # * Options with long descriptions have 1 blank line margin
    # * Long options have 1 blank line margin and description on next line.
    # * Other options have no margins.
    def test_src_width(self, assert_py_doc):
        assert_py_doc(
            settings=dict(line_width=66),
            text="""
            Top text.

            -a, --ax   Output all.
            -b         Output both (this description is
                       quite long).
            -c arg     Output just arg.
            --long     Output all day long.

            -p         This option has two paragraphs in the description.
                       This is the first.

                       This is the second.  Blank lines may be omitted between
                       options (as above) or left in (as here and below).

            --very-long-option  A VMS-style option.  Note the adjustment for
                                the required two spaces.

            --an-even-longer-option
                       The description can also start on the next line.

            -2, --two  This option has two variants.

            -f FILE, --file=FILE  These two options are synonyms; both have
                                  arguments.

            /V         A VMS/DOS-style option.

            Bottom text.
            """,
            expected="""
            Top text.

            -a, --ax   Output all.
            -b         Output both (this description is quite long).
            -c arg     Output just arg.
            --long     Output all day long.

            -p         This option has two paragraphs in the description. This
                       is the first.

                       This is the second. Blank lines may be omitted between
                       options (as above) or left in (as here and below).

            --very-long-option
                       A VMS-style option. Note the adjustment for the
                       required two spaces.

            --an-even-longer-option
                       The description can also start on the next line.

            -2, --two  This option has two variants.

            -f FILE, --file=FILE
                       These two options are synonyms; both have arguments.

            /V         A VMS/DOS-style option.

            Bottom text.
            """,
            pass_lines=True
        )

    # Test: if we pass all info + force margin between options.
    def test_margin(self, assert_py_doc):
        assert_py_doc(
            settings=dict(opt_margin=True, line_width=66),
            text="""
            Top text.

            -a, --ax   Output all.
            -b         Output both (this description is
                       quite long).
            -c arg     Output just arg.
            --long     Output all day long.

            -p         This option has two paragraphs in the description.
                       This is the first.

                       This is the second.  Blank lines may be omitted between
                       options (as above) or left in (as here and below).

            --very-long-option  A VMS-style option.  Note the adjustment for
                                the required two spaces.

            --an-even-longer-option
                       The description can also start on the next line.

            -2, --two  This option has two variants.

            -f FILE, --file=FILE  These two options are synonyms; both have
                                  arguments.

            /V         A VMS/DOS-style option.

            Bottom text.
            """,
            expected="""
            Top text.

            -a, --ax   Output all.

            -b         Output both (this description is quite long).

            -c arg     Output just arg.

            --long     Output all day long.

            -p         This option has two paragraphs in the description. This
                       is the first.

                       This is the second. Blank lines may be omitted between
                       options (as above) or left in (as here and below).

            --very-long-option
                       A VMS-style option. Note the adjustment for the
                       required two spaces.

            --an-even-longer-option
                       The description can also start on the next line.

            -2, --two  This option has two variants.

            -f FILE, --file=FILE
                       These two options are synonyms; both have arguments.

            /V         A VMS/DOS-style option.

            Bottom text.
            """,
            pass_lines=True
        )

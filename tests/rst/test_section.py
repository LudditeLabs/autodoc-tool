# Test: sections
class TestSection:
    # Test: sections with source code lines passed.
    def test_sections_with_src(self, assert_py_doc):
        assert_py_doc(
            text="""
            ===============
             Section Title
            ===============

            text

            ----------------
             Section Title1
            ----------------

            text1

            Section Title2
            ==============

            text2

            Section Title2
            ==============

            text2.1

            Section Title3
            --------------

            Section Title4
            ``````````````

            Section Title5
            ''''''''''''''

            Section Title6
            ..............

            Section Title7
            ~~~~~~~~~~~~~~

            Section Title8
            **************

            Section Title9
            ++++++++++++++

            Section Title10
            ^^^^^^^^^^^^^^^

            Section Title11
            %%%%%%%%%%%%%%%

            Section Title12
            ]]]]]]]]]]]]]]]
            """
        )

    # Test: sections without passing src lines.
    # In this case section markers will be calculated on sections levels.
    # But there is no way to detect if overline & padding is used.
    # Also sections styles are limited and has predefined order.
    def test_sections_no_src(self, assert_py_doc):
        # Without source code lines
        assert_py_doc(
            text="""
            ===============
             Section Title
            ===============

            text

            ----------------
             Section Title1
            ----------------

            text1

            Section Title2
            ==============

            text2

            Section Title2
            ==============

            text2.1

            Section Title3
            --------------

            Section Title4
            ``````````````

            Section Title5
            ''''''''''''''

            Section Title6
            ..............

            Section Title7
            ~~~~~~~~~~~~~~

            Section Title8
            **************

            Section Title9
            ++++++++++++++

            Section Title10
            ^^^^^^^^^^^^^^^

            Section Title11
            %%%%%%%%%%%%%%%

            Section Title11
            ]]]]]]]]]]]]]]]
            """,
            expected="""
            Section Title
            =============

            text

            Section Title1
            --------------

            text1

            Section Title2
            ``````````````

            text2

            Section Title2
            ::::::::::::::

            text2.1

            Section Title3
            ..............

            Section Title4
            ''''''''''''''

            Section Title5
            \"\"\"\"\"\"\"\"\"\"\"\"\"\"

            Section Title6
            ~~~~~~~~~~~~~~

            Section Title7
            ^^^^^^^^^^^^^^

            Section Title8
            ______________

            Section Title9
            **************

            Section Title10
            +++++++++++++++

            Section Title11
            ###############

            Section Title11
            ###############
            """,
            pass_lines=False
        )

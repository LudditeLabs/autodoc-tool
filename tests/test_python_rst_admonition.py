import pytest


@pytest.fixture(params=[False, True])
def pass_lines(request):
    """Simple fixture to yield False and True values for tests."""
    return request.param


# Test: common admonition.
class TestRstAdmonitionCommon:
    def test_complex(self, assert_py_doc, pass_lines):
        assert_py_doc(
            settings=dict(admonition_on_first_line=None, admonition_indent=0),
            pass_lines=pass_lines,
            text="""
            This is a paragraph.
    
            .. admonition:: And, by the way...
    
               You can make up your own admonition too.
    
            Some Text
    
            .. admonition:: And, by the way2...
    
               2You can make up your own admonition too.
    
            .. |subs| admonition:: And, by the way2...
    
               2You can make up your own admonition too.
            """)

    def test_simple(self, assert_py_doc, pass_lines):
        settings = dict(admonition_on_first_line=False, admonition_indent=0)
        assert_py_doc(
            settings=settings,
            pass_lines=pass_lines,
            text="""
            .. admonition:: And, by the way...

               You can make up your own admonition too.
            """,
            expected="""
            .. admonition::
               And, by the way...

               You can make up your own admonition too.
            """)

    # Test: admonition_blank_line is not used by the 'admonition'.
    def test_blank_line(self, assert_py_doc, pass_lines):
        settings = dict(admonition_on_first_line=False, admonition_indent=0,
                        admonition_blank_line=True)
        assert_py_doc(
            settings=settings,
            pass_lines=pass_lines,
            text="""
            .. admonition:: And, by the way...

               You can make up your own admonition too.
            """,
            expected="""
            .. admonition::
               And, by the way...

               You can make up your own admonition too.
            """)

    # Test: Auto detecting if we need to keep title on the same line or move
    # to next one. Line width = 50.
    def test_autodetect_title_50(self, assert_py_doc, pass_lines):
        settings = dict(admonition_on_first_line=None, admonition_indent=0,
                        admonition_blank_line=True, line_width=50)
        assert_py_doc(
            settings=settings,
            pass_lines=pass_lines,
            text="""
            .. admonition:: And, by the way... You can make up your own.

               You can make up your own admonition too.
            """,
            expected="""
            .. admonition::
               And, by the way... You can make up your own.

               You can make up your own admonition too.
            """)

    # Test: Auto detecting if we need to keep title on the same line or move
    # to next one. Line width = 150.
    def test_autodetect_title_150(self, assert_py_doc, pass_lines):
        settings = dict(admonition_on_first_line=None, admonition_indent=0,
                        admonition_blank_line=True, line_width=150)
        assert_py_doc(
            settings=settings,
            pass_lines=pass_lines,
            text="""
            .. admonition:: And, by the way... You can make up your own.

               You can make up your own admonition too.
            """)


# Test: admonition 'attention'.
class TestRstAdmonitionAttention:
    def test_autodetect_first_line(self, assert_py_doc, pass_lines):
        settings = dict(admonition_on_first_line=None, admonition_indent=0,
                        line_width=80)

        # Auto first line. Since we have no line width then always first line.
        assert_py_doc(
            settings=settings,
            pass_lines=pass_lines,
            text="""
            This is a paragraph.
    
            .. attention:: Lorem ipsum dolor sit amet, consectetur adipiscing elit.
               You can make up your own attention too.
    
            .. attention:: Lorem ipsum dolor sit amet, consectetur adipiscing elit.
    
               You can make up your own attention too.
            """,
            expected="""
            This is a paragraph.
    
            .. attention:: Lorem ipsum dolor sit amet, consectetur adipiscing elit. You can
               make up your own attention too.
    
            .. attention:: Lorem ipsum dolor sit amet, consectetur adipiscing elit.
    
               You can make up your own attention too.
            """
        )

    def test_no_first_line(self, assert_py_doc, pass_lines):
        settings = dict(admonition_on_first_line=False, admonition_indent=0)
        assert_py_doc(
            settings=settings,
            pass_lines=pass_lines,
            text="""
            .. attention:: And, by the way... You can make up your own.

               You can make up your own admonition too.
            """,
            expected="""
            .. attention::
               And, by the way... You can make up your own.

               You can make up your own admonition too.
            """)

    # Test: admonition_blank_line is not used by 'attention'.
    def test_blank_line(self, assert_py_doc, pass_lines):
        settings = dict(admonition_on_first_line=False, admonition_indent=0,
                        admonition_blank_line=True)
        assert_py_doc(
            settings=settings,
            pass_lines=pass_lines,
            text="""
            .. attention:: And, by the way... You can make up your own.

               You can make up your own admonition too.
            """,
            expected="""
            .. attention::

               And, by the way... You can make up your own.

               You can make up your own admonition too.
            """)

    # Test: Auto detecting if we need to keep title on the same line or move
    # to next one. Line width = 50.
    def test_autodetect_title_50(self, assert_py_doc, pass_lines):
        settings = dict(admonition_on_first_line=None, admonition_indent=0,
                        admonition_blank_line=False, line_width=50)
        assert_py_doc(
            settings=settings,
            pass_lines=pass_lines,
            text="""
            .. attention:: And, by the way... You can make up your own.

               You can make up your own admonition too.
            """,
            expected="""
            .. attention::
               And, by the way... You can make up your own.

               You can make up your own admonition too.
            """)

    # Test: Auto detecting if we need to keep title on the same line or move
    # to next one. Line width = 150.
    def test_autodetect_title_150(self, assert_py_doc, pass_lines):
        settings = dict(admonition_on_first_line=None, admonition_indent=0,
                        admonition_blank_line=False, line_width=150)
        assert_py_doc(
            settings=settings,
            pass_lines=pass_lines,
            text="""
            .. attention:: And, by the way... You can make up your own.

               You can make up your own admonition too.
            """)


# Test: remaining admonitions.
class TestRstAdmonitionRemaining:
    def test(self, assert_py_doc, pass_lines):
        settings = dict(admonition_on_first_line=False,
                        admonition_blank_line=False,
                        admonition_indent=2, line_width=62)
        assert_py_doc(
            settings=settings,
            pass_lines=pass_lines,
            text="""
            This is a paragraph.

            .. caution::
                 Lorem ipsum dolor sit amet, consectetur adipiscing elit.

                 sed do eiusmod tempor incididunt ut labore et dolore
                 magna aliqua. Ut enim ad minim veniam, quis nostrud
                 exercitation ullamco laboris nisi ut aliquip ex ea
                 commodo consequat.

                 Duis aute irure dolor in reprehenderit in voluptate velit
                 esse cillum dolore...

            .. danger::
                 Lorem ipsum dolor sit amet, consectetur adipiscing elit.

                 magna aliqua. Ut enim ad minim veniam, quis nostrud.

            .. error::
                 Lorem ipsum dolor sit amet, consectetur adipiscing elit.

                 magna aliqua. Ut enim ad minim veniam, quis nostrud.

            .. |substitution text| hint::
                 Lorem ipsum dolor sit amet, consectetur adipiscing elit.

                 magna aliqua. Ut enim ad minim veniam, quis nostrud.

            .. important::
                 Lorem ipsum dolor sit amet, consectetur adipiscing elit.

                 magna aliqua. Ut enim ad minim veniam, quis nostrud.

            .. note::
                 Lorem ipsum dolor sit amet, consectetur adipiscing elit.

                 magna aliqua. Ut enim ad minim veniam, quis nostrud.

            .. tip::
                 Lorem ipsum dolor sit amet, consectetur adipiscing elit.

                 magna aliqua. Ut enim ad minim veniam, quis nostrud.

            .. |substitution text| warning::
                 Lorem ipsum dolor sit amet, consectetur adipiscing elit.

                 magna aliqua. Ut enim ad minim veniam, quis nostrud.

            .. seealso::
                 magna aliqua. Ut enim ad minim veniam, quis nostrud.
            """)

    def test_wrap(self, assert_py_doc, pass_lines):
        settings = dict(admonition_on_first_line=False,
                        admonition_blank_line=False,
                        admonition_indent=2,
                        line_width=40)
        assert_py_doc(
            settings=settings,
            pass_lines=pass_lines,
            text="""
            This is a paragraph.

            .. caution::
                 Lorem ipsum dolor sit amet, consectetur adipiscing elit.

                 sed do eiusmod tempor incididunt ut labore et dolore
                 magna aliqua. Ut enim ad minim veniam, quis nostrud
                 exercitation ullamco laboris nisi ut aliquip
                 ex ea commodo consequat.

                 Duis aute irure dolor in reprehenderit in voluptate
                 velit esse cillum dolore...
            """,
            expected="""
            This is a paragraph.

            .. caution::
                 Lorem ipsum dolor sit amet,
                 consectetur adipiscing elit.

                 sed do eiusmod tempor incididunt ut
                 labore et dolore magna aliqua. Ut
                 enim ad minim veniam, quis nostrud
                 exercitation ullamco laboris nisi
                 ut aliquip ex ea commodo consequat.

                 Duis aute irure dolor in
                 reprehenderit in voluptate velit
                 esse cillum dolore...
            """)

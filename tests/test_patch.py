import pytest
from functools import partial
from autodoc.patch import Patch, LinePatcher
from autodoc.utils import trim_docstring

trim = partial(trim_docstring, strip_leading=True, strip_trailing=True,
               as_string=True)


# Test: Patch class.
class TestPatch:
    # Test: construct patch.
    def test_construct(self):
        patch = Patch('1\n2', 1, 2, 3, 4)
        assert patch.lines == ['1', '2']
        assert patch.start_line == 1
        assert patch.start_col == 2
        assert patch.end_line == 3
        assert patch.end_col == 4

    # Test: construct with 'None' content.
    def test_construct_none(self):
        patch = Patch(None, 1, 2, 3, 4)
        assert patch.lines is None
        assert patch.start_line == 1
        assert patch.start_col == 2
        assert patch.end_line == 3
        assert patch.end_col == 4


# Test: LinePatcher class.
class TestLinePatcher:
    # Test: construct patcher.
    def test_construct(self):
        patcher = LinePatcher()
        assert patcher._patches == []
        assert patcher._sorted is False

    # Test: add patch.
    def test_add(self):
        patcher = LinePatcher()

        patch = Patch('', 1, 1, 1, 1)
        patcher.add(patch)

        assert patcher._patches == [patch]
        assert patcher._sorted is False

    # Test: add multiple patches.
    def test_add_multiple(self):
        patcher = LinePatcher()

        patch = Patch('', 1, 1, 1, 1)
        patcher.add(patch)

        patch2 = Patch('', 1, 1, 1, 1)
        patcher.add(patch2)

        assert patcher._patches == [patch, patch2]
        assert patcher._sorted is False

    # Test: reset sorted flag on patch adding.
    def test_reset_sorted(self):
        patcher = LinePatcher()
        patcher._sorted = True

        patch = Patch('', 1, 1, 1, 1)
        patcher.add(patch)

        assert patcher._patches == [patch]
        assert patcher._sorted is False

    # Test: sort patches (in reverse mode).
    def test_sort(self):
        patcher = LinePatcher()

        p1 = Patch('', 1, 1, 1, 1)
        p2 = Patch('', 4, 1, 5, 1)
        p3 = Patch('', 2, 1, 2, 1)

        patcher.add(p1)
        patcher.add(p2)
        patcher.add(p3)
        patcher._sort_patches()

        assert patcher._sorted is True
        assert patcher._patches == [p2, p3, p1]

    # Test: apply empty list of patches. Must return the same content.
    def test_patch_empty(self):
        content = trim_docstring("""
        """, strip_leading=True, as_string=False)

        patcher = LinePatcher()
        assert patcher.patch(content) is content


# Test: original content without indentation.
class TestPatching:
    content = trim("""
        line 1
        line 2
        line 3
        line 4
        line 5
        """)

    # Test: insert patch before the line.
    @pytest.mark.parametrize("patches,expected", [
        ([Patch("xxx", 1, 1, None, None)],
         """
         xxx
         line 1
         line 2
         line 3
         line 4
         line 5
         """
         ),
        ([Patch("xxx", 3, 1, None, None)],
         """
         line 1
         line 2
         xxx
         line 3
         line 4
         line 5
         """
         ),
        ([Patch("xxx", 5, 1, None, None)],
         """
         line 1
         line 2
         line 3
         line 4
         xxx
         line 5
         """
         ),
        ([Patch("xxx", 6, 1, None, None)],  # Note: 6 - is out of bounds.
         """
         line 1
         line 2
         line 3
         line 4
         line 5
         xxx
         """
         ),
    ])
    def test_insert_before(self, patches, expected):
        patcher = LinePatcher(insert_after=False)
        for p in patches:
            patcher.add(p)
        assert '\n'.join(patcher.patch(self.content)) == trim(expected)

    # Test: insert patch before the line.
    @pytest.mark.parametrize("patches,expected", [
        ([Patch("xxx", 1, 1, None, None)],
         """
         line 1
         xxx
         line 2
         line 3
         line 4
         line 5
         """
         ),
        ([Patch("xxx", 3, 1, None, None)],
         """
         line 1
         line 2
         line 3
         xxx
         line 4
         line 5
         """
         ),
        ([Patch("xxx", 5, 1, None, None)],
         """
         line 1
         line 2
         line 3
         line 4
         line 5
         xxx
         """
         ),
        ([Patch("xxx", 6, 1, None, None)],  # Note: 6 - is out of bounds.
         """
         line 1
         line 2
         line 3
         line 4
         line 5
         xxx
         """
         ),
    ])
    def test_insert_after(self, patches, expected):
        patcher = LinePatcher()  # Insert after the line is default.
        for p in patches:
            patcher.add(p)
        assert '\n'.join(patcher.patch(self.content)) == trim(expected)

    @pytest.mark.parametrize("patches,expected", [
        # Patch one line with single line.
        ([Patch("xxx", 2, 1, 2, 7)],
         """
         line 1
         xxx
         line 3
         line 4
         line 5
         """
         ),
        # Patch 2 lines with single line.
        ([Patch("xxx", 2, 1, 3, 7)],
         """
         line 1
         xxx
         line 4
         line 5
         """
         ),
        # Patch one line partially with single line.
        ([Patch("xxx", 2, 3, 2, 5)],
         """
         line 1
         li
         xxx
          2
         line 3
         line 4
         line 5
         """
         ),
        # Patch one line partially with single line.
        ([Patch("xxx", 2, 3, 2, 7)],
         """
         line 1
         li
         xxx
         line 3
         line 4
         line 5
         """
         ),
        # Patch 2 lines partially with single line.
        ([Patch("xxx", 2, 3, 3, 7)],
         """
         line 1
         li
         xxx
         line 4
         line 5
         """
         ),
        # Patch 2 lines partially with single line.
        ([Patch("xxx", 2, 1, 3, 4)],
         """
         line 1
         xxx
         e 3
         line 4
         line 5
         """
         ),
        # Add single line after the position.
        ([Patch("xxx", 2, 1, None, None)],
         """
         line 1
         line 2
         xxx
         line 3
         line 4
         line 5
         """
         ),

        # Patch one line with multiple lines.
        ([Patch("xxx\nyyy", 2, 1, 2, 7)],
         """
         line 1
         xxx
         yyy
         line 3
         line 4
         line 5
         """
         ),
        # Patch 2 lines with multiple lines.
        ([Patch("xxx\nyyy", 2, 1, 3, 7)],
         """
         line 1
         xxx
         yyy
         line 4
         line 5
         """
         ),
        # Patch one line partially with multiple lines.
        ([Patch("xxx\nyyy", 2, 3, 2, 5)],
         """
         line 1
         li
         xxx
         yyy
          2
         line 3
         line 4
         line 5
         """
         ),
        # Patch one line partially with multiple lines.
        ([Patch("xxx\nyyy", 2, 3, 2, 7)],
         """
         line 1
         li
         xxx
         yyy
         line 3
         line 4
         line 5
         """
         ),
        # Patch 2 lines partially with multiple lines.
        ([Patch("xxx\nyyy", 2, 3, 3, 7)],
         """
         line 1
         li
         xxx
         yyy
         line 4
         line 5
         """
         ),
        # Patch 2 lines partially with multiple lines.
        ([Patch("xxx\nyyy", 2, 1, 3, 4)],
         """
         line 1
         xxx
         yyy
         e 3
         line 4
         line 5
         """
         ),
        # Add multiple lines after the position.
        ([Patch("xxx\nyyy", 2, 1, None, None)],
         """
         line 1
         line 2
         xxx
         yyy
         line 3
         line 4
         line 5
         """
         ),

        # Remove single line.
        ([Patch(None, 2, 1, 2, 7)],
         """
         line 1
         line 3
         line 4
         line 5
         """
         ),

        # Remove multiple line.
        ([Patch(None, 2, 1, 4, 7)],
         """
         line 1
         line 5
         """
         ),

        # Remove single line partially.
        ([Patch(None, 2, 1, 2, 3)],
         """
         line 1
         ne 2
         line 3
         line 4
         line 5
         """
         ),

        # Remove multiple lines partially.
        ([Patch(None, 2, 1, 3, 3)],
         """
         line 1
         ne 3
         line 4
         line 5
         """
         ),
        # Remove multiple lines partially, starting from middle.
        ([Patch(None, 2, 3, 3, 4)],
         """
         line 1
         li
         e 3
         line 4
         line 5
         """
         ),
    ])
    def test_patch(self, patches, expected):
        patcher = LinePatcher()
        for p in patches:
            patcher.add(p)
        assert '\n'.join(patcher.patch(self.content)) == trim(expected)

    content_indented = trim("""
        line 1
        line 2
          line 3
        line 4
        line 5
        """)

    @pytest.mark.parametrize("patches,expected", [
        # Patch one line with single line.
        # NOTE: here indent = 0 even if replaced line has indentation,
        # because start col = 1.
        ([Patch("xxx", 3, 1, 3, 9)],
         """
         line 1
         line 2
         xxx
         line 4
         line 5
         """
         ),
        # Patch 2 lines with single line.
        ([Patch("xxx", 3, 1, 4, 7)],
         """
         line 1
         line 2
         xxx
         line 5
         """
         ),
        # Patch one line partially with single line.
        # NOTE: right part of the line will have the same indentation.
        ([Patch("xxx", 3, 5, 3, 5)],
         """
         line 1
         line 2
           li
           xxx
           ne 3
         line 4
         line 5
         """
         ),
        # Patch one line partially with single line.
        ([Patch("xxx", 3, 5, 3, 7)],
         """
         line 1
         line 2
           li
           xxx
            3
         line 4
         line 5
         """
         ),
        # Patch 2 lines partially with single line.
        ([Patch("xxx", 3, 5, 4, 7)],
         """
         line 1
         line 2
           li
           xxx
         line 5
         """
         ),
        # Patch 2 lines partially with single line.
        ([Patch("xxx", 3, 1, 4, 4)],
         """
         line 1
         line 2
         xxx
         e 4
         line 5
         """
         ),
        # Add single line after the position.
        ([Patch("xxx", 3, 1, None, None)],
         """
         line 1
         line 2
           line 3
         xxx
         line 4
         line 5
         """
         ),
        # Add single line after the position.
        # NOTE: indentation detected from the start column of the patch.
        ([Patch("xxx", 3, 4, None, None)],
         """
         line 1
         line 2
           line 3
            xxx
         line 4
         line 5
         """
         ),

        # Patch one line with multiple lines.
        ([Patch("xxx\nyyy", 3, 3, 3, 100)],
         """
         line 1
         line 2
           xxx
           yyy
         line 4
         line 5
         """
         ),
        # Patch 2 lines with multiple lines.
        ([Patch("xxx\nyyy", 3, 3, 4, 9)],
         """
         line 1
         line 2
           xxx
           yyy
         line 5
         """
         ),
        # Patch one line partially with multiple lines.
        ([Patch("xxx\nyyy", 3, 5, 3, 5)],
         """
         line 1
         line 2
           li
           xxx
           yyy
           ne 3
         line 4
         line 5
         """
         ),
        # Patch one line partially with multiple lines.
        ([Patch("xxx\nyyy", 3, 5, 3, 9)],
         """
         line 1
         line 2
           li
           xxx
           yyy
         line 4
         line 5
         """
         ),
        # Patch 2 lines partially with multiple lines.
        ([Patch("xxx\nyyy", 3, 3, 4, 7)],
         """
         line 1
         line 2
           xxx
           yyy
         line 5
         """
         ),
        # Patch 2 lines partially with multiple lines.
        ([Patch("xxx\nyyy", 3, 1, 4, 4)],
         """
         line 1
         line 2
         xxx
         yyy
         e 4
         line 5
         """
         ),
        # Add multiple lines after the position.
        ([Patch("xxx\nyyy", 3, 2, None, None)],
         """
         line 1
         line 2
           line 3
          xxx
          yyy
         line 4
         line 5
         """
         ),
    ])
    def test_patch_indented(self, patches, expected):
        patcher = LinePatcher()
        for p in patches:
            patcher.add(p)
        assert '\n'.join(patcher.patch(self.content_indented)) == trim(expected)

import pytest
from functools import partial
from autodoc.patch import Patch, ContentPatcher
from autodoc.utils import trim_docstring

trim = partial(trim_docstring, strip_leading=True, strip_trailing=True,
               as_string=True)


# Test: Patch class.
class TestPatch:
    # Test: construct patch.
    def test_construct(self):
        patch = Patch('1\n2', 1, 2, 3, 4)
        assert patch.content == '1\n2'
        assert patch.start_line == 1
        assert patch.start_col == 2
        assert patch.end_line == 3
        assert patch.end_col == 4


# Test: ContentPatcher class.
class TestContentPatcher:
    # Test: construct patcher.
    def test_construct(self):
        patcher = ContentPatcher()
        assert patcher._patches == []
        assert patcher._sorted is False

    # Test: add patch.
    def test_add(self):
        patcher = ContentPatcher()

        patch = Patch('', 1, 1, 1, 1)
        patcher.add(patch)

        assert patcher._patches == [patch]
        assert patcher._sorted is False

    # Test: add multiple patches.
    def test_add_multiple(self):
        patcher = ContentPatcher()

        patch = Patch('', 1, 1, 1, 1)
        patcher.add(patch)

        patch2 = Patch('', 1, 1, 1, 1)
        patcher.add(patch2)

        assert patcher._patches == [patch, patch2]
        assert patcher._sorted is False

    # Test: reset sorted flag on patch adding.
    def test_reset_sorted(self):
        patcher = ContentPatcher()
        patcher._sorted = True

        patch = Patch('', 1, 1, 1, 1)
        patcher.add(patch)

        assert patcher._patches == [patch]
        assert patcher._sorted is False

    # Test: sort patches (in reverse mode).
    def test_sort(self):
        patcher = ContentPatcher()

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
        """, strip_leading=True, as_string=True)

        patcher = ContentPatcher()
        assert patcher.patch(content) is content


# Test: patching text.
class TestPatching:
    # Original text.
    text = trim("""
    Line 1
    Line 2
    Line 3
    Line 4
    Line 5
    """)

    @pytest.mark.parametrize("patches,expected", [

        # Single patch.

        # Test: replace two lines with a single one.
        # NOTE: end col is too big, but it's fine.
        ([Patch('!hello!', 2, 1, 3, 70)],
         """
         Line 1
         !hello!
         Line 4
         Line 5
         """
         ),

        # Test: replace two lines partially.
        ([Patch('!hello!', 2, 1, 3, 5)],
         """
         Line 1
         !hello! 3
         Line 4
         Line 5
         """
         ),

        # Test: insert a text to the beginning of the line.
        ([Patch('!hello!', 2, 1, 2, 1)],
         """
         Line 1
         !hello!Line 2
         Line 3
         Line 4
         Line 5
         """
         ),

        # Test: insert multiple lines to the beginning of the line
        ([Patch('!hello!\n123', 2, 1, 2, 1)],
         """
         Line 1
         !hello!
         123Line 2
         Line 3
         Line 4
         Line 5
         """
         ),

        # Test: replace a line partially with two lines.
        ([Patch('!hello!\n1-', 2, 1, 2, 3)],
         """
         Line 1
         !hello!
         1-ne 2
         Line 3
         Line 4
         Line 5
         """
         ),

        # Multiple patches.

        ([Patch('--', 1, 2, 1, 5), Patch('!hello!\n123', 2, 1, 2, 1)],
         """
         L-- 1
         !hello!
         123Line 2
         Line 3
         Line 4
         Line 5
         """
         ),
    ])
    def test_patch(self, patches, expected):
        patcher = ContentPatcher()
        for p in patches:
            patcher.add(p)
        assert patcher.patch(self.text) == trim(expected)

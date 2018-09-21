"""
This module implements simple patching feature.
"""
from docutils.io import FileInput, FileOutput
from .utils import as_lines, get_indent


class Patch:
    """This class represents a patch."""
    __slots__ = ('lines', 'start_line', 'start_col', 'end_line', 'end_col')

    def __init__(self, content, start_line, start_col, end_line, end_col):
        """Construct patch.

        If ``end_line`` and ``end_col`` are not set (``None``) then ``lines``
        will be inserted to ``start_line`` or after it (depending on patcher
        flag ``insert_after``).

        Args:
            content: String or list of strings.
            start_line: Start line.
            start_col: Start column.
            end_line: End line.
            end_col: End column.
        """
        self.lines = as_lines(content)
        self.start_line = start_line
        self.start_col = start_col
        self.end_line = end_line
        self.end_col = end_col


class LinePatcher:
    """This class applies list of patched on original content.

    It also auto indents patch lines depending on where it applied.
    Patch content is always inserts starting from new line.

    If a patch inserts content in the middle of a line then the line is
    split into two lines and the content inserts between them.
    """
    def __init__(self, insert_after=True):
        """Construct patcher.

        Args:
            insert_after: Insert patch after the source line.
        """
        self._patches = []
        self._sorted = False
        self._insert_after = insert_after

    def _sort_patches(self):
        """Sort patches in reverse order based on start positions."""
        self._patches.sort(key=lambda x: x.start_line, reverse=True)
        self._sorted = True

    def add(self, patch):
        """Add patch to apply.

        Args:
            patch: :class:`Patch` instance.
        """
        self._patches.append(patch)
        self._sorted = False

    # NOTE: positions in patch are 1-based.
    def patch(self, content):
        """Patch given ``content``.

        Args:
            content: String or list of strings.

        Returns:
            Patched list of strings.
        """
        lines = as_lines(content)

        if not self._patches:
            return lines
        if not self._sorted:
            self._sort_patches()

        for patch in self._patches:
            # Insert lines.
            if patch.end_line is None:
                indent = patch.start_col - 1
                if indent:
                    offset = ' ' * indent
                    patch_lines = [offset + x for x in patch.lines]
                else:
                    patch_lines = patch.lines
                pos = patch.start_line
                if not self._insert_after:
                    pos -= 1
                lines[pos:pos] = patch_lines
                continue

            col = patch.start_col - 1
            start = patch.start_line - 1
            end = patch.end_line
            to_insert = None

            first = lines[start]
            first_part = first[:col]
            first_indent = get_indent(first_part)

            if first_part and len(first_part) != first_indent:
                to_insert = [first_part]
                indent = first_indent
            else:
                indent = col

            if indent:
                offset = ' ' * indent
                patch_lines = [offset + x for x in patch.lines]
            else:
                patch_lines = patch.lines

            if to_insert:
                to_insert.extend(patch_lines)
            else:
                to_insert = patch_lines

            last = lines[end - 1]
            last_part = last[patch.end_col - 1:]
            if last_part and not last_part.isspace():
                if first_indent:
                    last_part = ' ' * first_indent + last_part
                to_insert.append(last_part)

            lines[start:end] = to_insert

        return lines


class FilePatcher:
    """This class applies patches to a file."""
    def __init__(self, filename, encoding=None, insert_after=True):
        """Construct file patcher.

        Args:
            filename: Filename to patch.
            encoding: File encoding.
            insert_after: Insert patch after the source line.
        """
        self._filename = filename
        self._encoding = encoding
        self._patcher = LinePatcher(insert_after=insert_after)

    def add(self, patch):
        """Add patch.

        Args:
            patch: :class:`Patch` instance.
        """
        self._patcher.add(patch)

    def patch(self, out_filename=None):
        """Apply patches and write changes to specified file.

        Args:
            out_filename: Output filename. If not set then input one is used.
        """
        in_ = FileInput(source_path=self._filename, encoding=self._encoding)
        content = in_.read()
        content = self._patcher.patch(content)
        content = '\n'.join(content)

        out = FileOutput(destination_path=out_filename or self._filename,
                         encoding=self._encoding)
        out.write(content)

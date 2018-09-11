"""
This module implements simple patching feature.
"""


class Patch:
    """This class represents a content patch."""
    __slots__ = ('content', 'start_line', 'start_col', 'end_line', 'end_col')

    def __init__(self, content, start_line, start_col, end_line, end_col):
        """Construct patch.

        Args:
            content: Patch content.
            start_line: Start line.
            start_col: Start column.
            end_line: End line.
            end_col: End column.
        """
        self.content = content
        self.start_line = start_line
        self.start_col = start_col
        self.end_line = end_line
        self.end_col = end_col


class ContentPatcher:
    """This class applies list of patched on original content.

    How it works:

    * Split original text into lines.

    * For each patch it merge original lines ``[start_line; end_line]``
      into string.

    * Replace content in the string in the range ``[start_col; end_col)``.

    * Converts result string into lines and replace original lines.
    """
    def __init__(self):
        self._patches = []
        self._sorted = False

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

    # TODO: improve, this may be not very optimal.
    def patch(self, content):
        """Apply patches on the given content.

        Args:
            content: Content to patch.

        Returns:
            Patched content.
        """
        if not self._patches:
            return content
        if not self._sorted:
            self._sort_patches()

        lines = content.splitlines(False)

        # NOTE: positions in patch are 1-based.
        for patch in self._patches:
            # Create slice to replace.
            s = slice(patch.start_line - 1, patch.end_line)

            # Text to replace.
            txt = '\n'.join(lines[s])

            # Replace left part.
            newtxt = txt[:patch.start_col - 1] + patch.content

            # Add right part if required.
            #
            # 'end' is index of remaining chars from the right side
            # of the last line.
            end = len(lines[patch.end_line - 1]) - patch.end_col + 1
            if end:
                newtxt += txt[-end:]

            # Convert back to lines and replace original ones.
            lines[s] = newtxt.splitlines(False)

        return '\n'.join(lines)

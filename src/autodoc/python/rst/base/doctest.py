"""
Doctest Blocks
--------------

Doctest blocks are text blocks which begin with ">>> ", the Python interactive
interpreter main prompt, and end with a blank line.

Doctest blocks are treated as a special case of literal blocks,
without requiring the literal block syntax.

If both are present, the literal block syntax takes priority
over Doctest block syntax.

http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html#doctest-blocks
"""


class DoctestMixin:
    def visit_doctest_block(self, node):
        self.open_block(top_margin=1, bottom_margin=1, no_wrap=True)

    def depart_doctest_block(self, node):
        self.close_block()

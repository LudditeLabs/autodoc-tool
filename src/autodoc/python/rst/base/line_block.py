"""
Line Blocks
-----------

Line blocks are groups of lines beginning with vertical bar ("|") prefixes.
Each vertical bar prefix indicates a new line, so line breaks are preserved.
Initial indents are also significant, resulting in a nested structure.
Inline markup is supported. Continuation lines are wrapped portions
of long lines; they begin with a space in place of the vertical bar.
The left edge of a continuation line must be indented, but need not be aligned
with the left edge of the text above it. A line block ends with a blank line.

Syntax diagram:

    +------+-----------------------+
    | "| " | line                  |
    +------| continuation line     |
           +-----------------------+

http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html#line-blocks
"""


# TODO: align continuation line as in original source.
# Currently we always align with the above line.
# Docs says:
#     The left edge of a continuation line must be indented,
#     but need not be aligned with the left edge of the text above it.
class LineBlockMixin:
    def visit_line_block(self, node):
        # Line blocks must ends with a blank line + we don't wrap it.
        self.open_block(top_margin=0, bottom_margin=0, no_wrap=True)

    def depart_line_block(self, node):
        # Indent continuation line.
        lines = self.block.lines
        for i in range(len(lines)):
            if not lines[i].startswith('|'):
                lines[i] = u'  ' + lines[i]
        self.close_block()

    def visit_line(self, node):
        if not self.block.is_empty():
            self.block.add_text(u'\n')
        self.block.add_text(u'| ')

    def depart_line(self, node):
        pass

"""
Block Quotes
------------

Line blocks are groups of lines beginning with vertical bar ("|") prefixes.
Each vertical bar prefix indicates a new line, so line breaks are preserved.
Initial indents are also significant, resulting in a nested structure.
Inline markup is supported. Continuation lines are wrapped portions
of long lines; they begin with a space in place of the vertical bar.
The left edge of a continuation line must be indented, but need not be aligned
with the left edge of the text above it. A line block ends with a blank line.

Syntax diagram:

    +------------------------------+
    | (current level of            |
    | indentation)                 |
    +------------------------------+
       +---------------------------+
       | block quote               |
       | (body elements)+          |
       |                           |
       | -- attribution text       |
       |    (optional)             |
       +---------------------------+

http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html#block-quotes
"""


class BlockQuoteMixin:
    def visit_block_quote(self, node):
        self.open_block(indent=self.options['indent'], top_margin=1,
                        bottom_margin=1)

    def depart_block_quote(self, node):
        self.close_block()

    def visit_attribution(self, node):
        self.block.add_text(u'-- ')

    def depart_attribution(self, node):
        pass

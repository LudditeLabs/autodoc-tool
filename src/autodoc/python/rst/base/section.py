"""
Sections
--------

This module implements sections support.

http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html#sections
"""
from docutils import nodes


# Recommendations:
# # with overline, for parts
# * with overline, for chapters
# =, for sections
# -, for subsections
# ^, for subsubsections
# ", for paragraphs
class SectionMixin:
    section_styles = '=-`:.\'"~^_*+#'

    def visit_section(self, node):
        level = self.states.get('section', -1)
        self.states['section'] = level + 1

    def depart_sections(self, node):
        self.states['section'] -= 1

    # NOTE: title is used in other directives too.
    def visit_title(self, node):
        i = node.line - 1
        # NOTE: admonition directive also uses title.
        # It doesn't initialize states['section'] like visit_section() does.
        # So we use get() method here and return -1 by default.
        level = self.states.get('section', -1)

        if level != -1:
            if self.source_lines and i < self.num_source_lines:
                underline = self.source_lines[i]
                overline = self.source_lines[i-2] if i >= 2 else None
                text = node.astext().center(len(underline))

                # TODO: make margins configurable.
                self.open_block(top_margin=1, bottom_margin=1)
                if overline:
                    self.block.add_boxed(overline)
                    self.block.add_boxed('\n')
                self.block.add_boxed(text)
                self.block.add_boxed('\n')
                self.block.add_boxed(underline)
                self.close_block()
                raise nodes.SkipNode
            else:
                if level >= len(self.section_styles):
                    level = len(self.section_styles) - 1
                style = self.section_styles[level]

                # TODO: make margins configurable.
                self.open_block(top_margin=1, bottom_margin=1)
                text = node.astext()
                marker = style * len(text)
                self.block.add_boxed(text)
                self.block.add_boxed('\n')
                self.block.add_boxed(marker)
                self.close_block()
                raise nodes.SkipNode

    def depart_title(self, node):
        pass

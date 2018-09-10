"""
Admonitions
-----------

http://docutils.sourceforge.net/docs/ref/rst/directives.html#admonitions
"""
from docutils import nodes


class AdmonitionMixin:
    # Admonition has title and content.
    #     .. admonition: <title>
    #
    #        <content>
    #
    # or:
    #     .. admonition:
    #        <title>
    #
    #        <content>
    #
    # Other admonitions:
    #
    # .. <name>::
    #    Beware killer rabbits!
    #
    # TODO: add options support :name: and :class:
    # http://docutils.sourceforge.net/docs/ref/rst/directives.html#admonitions
    def visit_common_admonition(self, node):
        # Substitution definition.
        alt = node.get('alt')
        if alt is not None:
            prefix = u'.. |{}| {}::'.format(alt, node.tagname)
        else:
            prefix = u'.. {}::'.format(node.tagname)

        line_width = self.block_mgr.last_width

        # TODO: have separate config for each admonition type.
        admonition_on_first_line = self.options['admonition_on_first_line']

        if node.tagname == 'admonition':
            admonition_blank_line = False
        else:
            admonition_blank_line = self.options['admonition_blank_line']

        same_line = False

        # Auto.
        if admonition_on_first_line is None:
            if line_width is None:
                same_line = True  # put on the same line.
            elif node.children:
                # If text has multiple lines, check if first one fits to width.
                txt = node.children[0].rawsource
                if txt:
                    txt = txt.split('\n', 1)[0]
                    sz = len(txt) + len(prefix) + 1
                    if sz <= line_width:
                        same_line = True
        elif admonition_on_first_line is True:
            same_line = True

        indent = 3 + self.options['admonition_indent']

        if same_line:
            bottom_margin = None
        elif admonition_blank_line:
            bottom_margin = 1
        else:
            bottom_margin = 0

        self.open_block(top_margin=0, bottom_margin=bottom_margin,
                        child_indent=indent, next=dict(top_margin=0))
        self.block.add_boxed(prefix)

        # If there is a title then we open new block to apply top_margin=0
        # and bottom_margin to it.
        if isinstance(node.children[0], nodes.title):
            self.open_block()

    def depart_common_admonition(self, node):
        # We opened extra block for the title, so must close.
        if isinstance(node.children[0], nodes.title):
            self.close_block()
        self.close_block()

    visit_admonition = visit_common_admonition
    depart_admonition = depart_common_admonition

    visit_attention = visit_common_admonition
    depart_attention = depart_common_admonition

    visit_caution = visit_common_admonition
    depart_caution = depart_common_admonition

    visit_danger = visit_common_admonition
    depart_danger = depart_common_admonition

    visit_error = visit_common_admonition
    depart_error = depart_common_admonition

    visit_hint = visit_common_admonition
    depart_hint = depart_common_admonition

    visit_important = visit_common_admonition
    depart_important = depart_common_admonition

    visit_note = visit_common_admonition
    depart_note = depart_common_admonition

    visit_tip = visit_common_admonition
    depart_tip = depart_common_admonition

    visit_warning = visit_common_admonition
    depart_warning = depart_common_admonition

    visit_seealso = visit_common_admonition
    depart_seealso = depart_common_admonition

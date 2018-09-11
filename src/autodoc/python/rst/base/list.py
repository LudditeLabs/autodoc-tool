"""
Bullet & enum list
------------------

http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html#bullet-lists
http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html#enumerated-lists
"""


# http://code.activestate.com/recipes/81611-roman-numerals/
def int_to_roman(val):
    """Helper function to convert integer to roman number."""
    if not 0 < val < 4000:
        val = 3999
    ints = (1000, 900,  500, 400, 100,  90, 50,  40, 10,  9,   5,  4,   1)
    nums = ('M', 'CM', 'D', 'CD', 'C', 'XC', 'L', 'XL', 'X', 'IX', 'V', 'IV',
            'I')
    result = ''

    for i in range(len(ints)):
        count = int(val / ints[i])
        result += nums[i] * count
        val -= ints[i] * count
    return result


class ListMixin:
    def visit_bullet_list(self, node):
        # [etype, prefix, val, suffix, indent]
        state = self.states.setdefault('list_state', [])
        state.append(['bullet', None, node['bullet'], None])

    def depart_bullet_list(self, node):
        # list_state must be created in the visit_bullet_list().
        self.states['list_state'].pop()

    def visit_list_item(self, node):
        top = bottom = 1
        sub_node = node.children[0]

        # Check if items are separated with blank line.
        if self.source_lines:
            # -1 to make it zero based
            # -1 to get prev line.
            if sub_node.line is not None:
                pos = sub_node.line - 1 - 1
            else:
                pos = -1
            if pos >= 0:
                if self.source_lines[pos].strip():
                    top = bottom = 0
                else:
                    top = 1
                    bottom = 0

        list_state = self.states['list_state'][-1]

        if list_state[0] == 'bullet':
            bullet = list_state[2]
        elif list_state[0] == 'arabic':
            bullet = u'{}{}{}'.format(list_state[1], list_state[2],
                                      list_state[3])
            list_state[2] += 1
        elif list_state[0] in ('loweralpha', 'upperalpha'):
            bullet = u'{}{}{}'.format(list_state[1], list_state[2],
                                      list_state[3])
            if list_state[2] in ('z', 'Z'):
                pass
            else:
                list_state[2] = chr(ord(list_state[2]) + 1)
        elif list_state[0] in ('upperroman', 'lowerroman'):
            val = int_to_roman(list_state[2])
            if list_state[2] < 3999:
                list_state[2] += 1
            bullet = u'{}{}{}'.format(list_state[1], val, list_state[3])
            if list_state[0].startswith('l'):
                bullet = bullet.lower()
        else:
            bullet = u''

        indent = len(bullet) + 1

        if top == 0:
            top = None

        self.open_block(top_margin=top, bottom_margin=bottom,
                        child_indent=indent, next=dict(top_margin=None))

        # Make sure we merge from new line.
        if top is None:
            self.block.merge_to_new_line = True

        self.block.add_boxed(bullet)

    def depart_list_item(self, node):
        self.close_block()

    def visit_enumerated_list(self, node):
        state = self.states.setdefault('list_state', [])
        etype = node['enumtype']
        prefix = node['prefix']
        suffix = node['suffix']
        val = None
        if etype in ('arabic', 'upperroman', 'lowerroman'):
            val = 1
        elif etype == 'loweralpha':
            val = u'a'
        elif etype == 'upperalpha':
            val = u'A'

        # Inherit indent of the parent list.
        if state:
            indent = state[-1][4]
        else:
            indent = 0

        state.append([etype, prefix, val, suffix, indent])

    def depart_enumerated_list(self, node):
        # list_state must be created in the visit_enumerated_list().
        self.states['list_state'].pop()

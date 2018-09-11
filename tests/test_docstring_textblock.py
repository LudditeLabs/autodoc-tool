import pytest
from autodoc.docstring.textblock import (
    BaseBlock,
    LineBlock,
    WrapBlock,
    BlockManager
)


# Test: BaseBlock - base class for text block.
class TestBaseBlock:
    # Test: BaseBlock constructor.
    def test_construct(self):
        b = BaseBlock()
        assert b.indent == 0
        assert b.first_offset is None
        assert b.child_indent == 0
        assert b.width is None
        assert b.top_margin == 0
        assert b.bottom_margin == 0

        b = BaseBlock(1, 2, 3, 4, 5, 6)
        assert b.indent == 1
        assert b.first_offset == 2
        assert b.child_indent == 3
        assert b.width == 3  # initial width (4) - indent 1
        assert b.top_margin == 5
        assert b.bottom_margin == 6

        assert b.is_empty()
        assert not b.is_box_started()


# Test: LineBlock - block of lines without wrapping.
class TestLineBlock:
    # Test: LineBlock constructor.
    def test_construct(self):
        b = LineBlock()
        assert b.indent == 0
        assert b.first_offset is None
        assert b.child_indent == 0
        assert b.width is None
        assert b.top_margin == 0
        assert b.bottom_margin == 0
        assert b.lines == []

        b = LineBlock(1, 2, 3, 4, 5, 6)
        assert b.indent == 1
        assert b.first_offset == 2
        assert b.child_indent == 3
        assert b.width == 3
        assert b.top_margin == 5
        assert b.bottom_margin == 6
        assert b.lines == []

        assert b.is_empty()
        assert not b.is_box_started()

    # Test: add single line.
    def test_add(self):
        block = LineBlock()

        # Add to empty block - just add it a a line.
        block.add_text('text')
        assert block.lines == ['text']

        assert not block.is_empty()

        # Add to non empty block - add it to the last line.
        block.add_text('-xx')
        assert block.lines == ['text-xx']

        # Add empty - add nothing to the last line
        block.add_text('')
        assert block.lines == ['text-xx']

        # Same as add_text()
        block.add_boxed('boxed')
        assert block.lines == ['text-xxboxed']

        # Add empty string to empyt block.
        block = LineBlock()
        block.add_text('')
        assert block.lines == ['']

    # Test: add multi line text.
    def test_add_multiline(self):
        block = LineBlock()

        # Add to empty block - add to the end of the block.
        block.add_text('1\n2')
        assert block.lines == ['1', '2']

        # Add to non empty block:
        # first line add to the block's end line
        # the rest add as a separate lines.
        block.add_text('3\n4\n5')
        assert block.lines == ['1', '23', '4', '5']

        # Add list with first blank line - add as a separate lines.
        block.add_text('\n6')
        assert block.lines == ['1', '23', '4', '5', '6']

        block.add_text('\n')
        assert block.lines == ['1', '23', '4', '5', '6', '']

        # Add to the block where last line is blank.
        block.add_text('7\n8\n')
        assert block.lines == ['1', '23', '4', '5', '6', '7', '8', '']

        block.add_text('9')
        assert block.lines == ['1', '23', '4', '5', '6', '7', '8', '9']

    # Test: LineBlock clear.
    def test_clear(self):
        block = LineBlock()
        block.add_text('9')
        block.clear()
        assert block.lines == []
        assert block.is_empty()

    # Test: get result lines without indentation.
    def test_get(self):
        block = LineBlock()
        block.add_text('This paragraph will result')
        block.add_text(' in an indented block of\n')
        block.add_text('Another top-level paragraph\nBla bla')

        pytest.g.assert_lines(
            list(block.get_lines()),
            ['This paragraph will result in an indented block of',
             'Another top-level paragraph',
             'Bla bla'])


# Test: WrapBlock - block of lines with wrapping.
class TestWrapBlock:
    # Test: LineBlock constructor.
    def test_construct(self):
        b = WrapBlock()
        assert b.indent == 0
        assert b.first_offset is None
        assert b.child_indent == 0
        assert b.width is None
        assert b.top_margin == 0
        assert b.bottom_margin == 0
        assert b.words == []
        assert b._box is None
        assert not b.is_box_started()
        assert list(b.get_lines()) == []

        b = WrapBlock(1, 2, 3, 4, 5, 6)
        assert b.indent == 1
        assert b.first_offset == 2
        assert b.child_indent == 3
        assert b.width == 3
        assert b.top_margin == 5
        assert b.bottom_margin == 6
        assert b.words == []
        assert b._box is None

        assert not b.is_box_started()
        assert b.is_empty()

    # Test: add single line.
    def test_add(self):
        block = WrapBlock()

        # Add to empty block - just add it a a line.
        block.add_text('text')
        assert block.words == ['text']

        assert not block.is_empty()

        # Add to non empty block - add it to the last line.
        block.add_text('-xx')
        assert block.words == ['text', '-xx']
        assert not block.is_box_started()

        # Add empty - add nothing to the last line
        block.add_text('')
        assert block.words == ['text', '-xx']

        # Add multiple words.
        block.add_text('two words')
        assert block.words == ['text', '-xx', 'two', 'words']

        # This adds empty word which will be skipped in further processing.
        block.add_text('\n')
        # assert block.words == ['text', '-xx', 'two', 'words', '']
        assert block.words == ['text', '-xx', 'two', 'words']

        # Add empty string to empyt block.
        block = WrapBlock()
        block.add_text('')
        assert block.words == []

    # Test: add boxed text (protected with wrapping).
    def test_add_boxed(self):
        block = WrapBlock()
        block.add_text('one two')

        # Internal list is not set by default.
        assert block._box is None

        # Add boxed in one call.
        block.add_boxed('b x')
        assert block.words == ['one', 'two', ['b x']]

        # Internal list is reset after the call.
        assert block._box is None

        # Add boxed with explicit start/end.
        block.start_box()

        # Internal list is initialized now.
        assert block._box == []
        assert block.is_box_started()

        # And boxed list is added right after the call.
        assert block.words == ['one', 'two', ['b x'], []]

        # These words will be added after the boxed.
        block.add_text('one')
        block.add_text('two')

        # Still not added to the words.
        assert block.words == ['one', 'two', ['b x'], ['one', 'two']]

        # But internal box list if filled.
        assert block._box == ['one', 'two']

        # Do nothing if already started.
        block.start_box()
        assert block._box == ['one', 'two']

        block.end_box()
        assert not block.is_box_started()
        assert block._box is None
        assert block.words == ['one', 'two', ['b x'], ['one', 'two']]

        # Don't add empty box to words.
        block.start_box()
        block.end_box()
        assert block.words == ['one', 'two', ['b x'], ['one', 'two'], []]

        block.start_box()
        block.add_boxed('1')
        block.add_text('2')
        block.end_box()
        assert block.words == ['one', 'two', ['b x'], ['one', 'two'], [],
                               ['2'], ['1']]

        # This will force line break.
        block.add_boxed('\n')
        assert block.words == ['one', 'two', ['b x'], ['one', 'two'], [],
                               ['2'], ['1'], '\n']

    # Test: add multi line text.
    def test_add_multiline(self):
        block = WrapBlock()

        # Add to empty block - add to the end of the block.
        block.add_text('1\n2')
        assert block.words == ['1', '2']

        # Add to non empty block:
        block.add_text('3\n4\n5')
        assert block.words == ['1', '2', '3', '4', '5']

        # Add list with first blank line - it will skipped.
        block.add_text('\n6')
        assert block.words == ['1', '2', '3', '4', '5', '6']

        # Single '\n' is skipped too.
        block.add_text('\n')
        assert block.words == ['1', '2', '3', '4', '5', '6']

        # In this case first \n will be stripped.
        block.add_text('\n\n')
        # First \n forces line break and second one forces blank line
        assert block.words == ['1', '2', '3', '4', '5', '6', '\n', '\n']

        # Add to the block where last line is blank.
        block.add_text('7\n8\n')
        assert block.words == ['1', '2', '3', '4', '5', '6', '\n', '\n', '7',
                               '8']

        block.add_text('9')
        assert block.words == ['1', '2', '3', '4', '5', '6', '\n', '\n', '7',
                               '8', '9']

        block.add_text('10 11\n 12\n13')
        assert block.words == ['1', '2', '3', '4', '5', '6', '\n', '\n', '7',
                               '8', '9', '10', '11', '12', '13']

        block.clear()
        block.add_text('1\n 2\n\n3')
        assert block.words == ['1', '2', '\n', '\n', '3']

    # Test: clear WrapBlock.
    def test_clear(self):
        block = WrapBlock(parent_width=20)
        block.add_text('This paragraph will result in an indented block of')
        block.start_box()
        block.add_text('sss')
        block.clear()
        assert block.words == []
        assert block._box is None
        assert block.is_empty()

    # Test: simple wrapping, no indentation.
    def test_simple(self):
        block = WrapBlock(parent_width=20)
        block.add_text('This paragraph will result in an indented block of')
        block.add_text('Another top-level paragraph')
        pytest.g.assert_lines(
            list(block.get_lines()),
            ['This paragraph will',
             'result in an',
             'indented block of',
             'Another top-level',
             'paragraph'])

    # Test: wrapping with empty words
    def test_simple_empty_words(self):
        block = WrapBlock(parent_width=20)
        # Add empty box.
        block.start_box()
        block.end_box()
        block.add_text('This paragraph will result \nin an indented block of')
        block.add_text('Another top-level paragraph')
        pytest.g.assert_lines(
            list(block.get_lines()),
            ['This paragraph will',
             'result in an',
             'indented block of',
             'Another top-level',
             'paragraph'])

    # Test: first line must have smaller width.
    def test_first_offset(self):
        block = WrapBlock(first_offset=10, parent_width=30)
        block.add_text('This paragraph will result in an indented block of')
        block.add_text('Another top-level paragraph')

        pytest.g.assert_lines(
            list(block.get_lines()),
            ['This paragraph will',
             'result in an indented block of',
             'Another top-level paragraph'])

    # Test: wrapping with protected block.
    def test_box(self):
        block = WrapBlock(parent_width=28)
        block.add_text('This paragraph will result in an indented block')
        block.add_boxed('of Another')
        block.add_text('top-level paragraph')
        block.start_box()
        block.add_text('protected')
        block.add_text('text')
        block.end_box()

        # NOTE: words between start_box() and end_box() is joined without space.
        pytest.g.assert_lines(
            list(block.get_lines()),
            ['This paragraph will result',
             'in an indented block',
             'of Another top-level',
             'paragraph protectedtext'])

    # Test: wrap long protected box.
    def test_box_long(self):
        block = WrapBlock(parent_width=8)
        block.add_boxed('a' * 12)
        pytest.g.assert_lines(list(block.get_lines()), ['a' * 12])

    def test_line_break(self):
        block = WrapBlock(parent_width=28)
        block.add_text('This paragraph will result in an indented block')
        block.add_text('top-')
        block.add_boxed('\n')  # Force line break
        block.add_text('level paragraph')
        block.add_boxed('\n')  # Force line break
        block.add_boxed('\n')  # Force line break
        block.add_text('protected text')
        block.add_boxed('\n')  # Force line break
        block.add_boxed('\n')  # Force line break
        pytest.g.assert_lines(
            list(block.get_lines()),
            ['This paragraph will result',
             'in an indented block top-',
             'level paragraph',
             '',
             'protected text',
             '',
             ''])


# Test: how WrapBlock handles various punctuations.
class TestWrapBlockPunctuation:
    # Test: one line simple cases.
    # data: last string is expected text line
    #       and others are words; list means boxed word.
    @pytest.mark.parametrize('data', [
        # -- punctuation before boxed word ------------------------------------
        #
        # Only ``WrapBlock.enclose_start`` chars are takes in account.

        ('See (', [':func:`foo`'],          'See (:func:`foo`'),
        ('See [ ', [':func:`foo`'],         'See [:func:`foo`'),
        ('See { {', [':func:`foo`'],        'See { {:func:`foo`'),

        # ' and " before boxed word.
        ('See "', [':func:`foo`'],          'See ":func:`foo`'),
        ("See '", [':func:`foo`'],          "See ':func:`foo`"),
        ("'See'", ['http://ex.com'],        "'See' http://ex.com"),
        ("See'", ['http://ex.com'],         "See'http://ex.com"),

        # NOTE: ':', ')' are not an enclosing chars so there must be space.
        ('See:', [':func:`foo`'],           'See: :func:`foo`'),
        ('See)', [':func:`foo`'],           'See) :func:`foo`'),
        ('See', ')', [':func:`foo`'],       'See ) :func:`foo`'),

        # -- punctuation after boxed word -------------------------------------
        # Only ``WrapBlock.punctuation_end`` chars are takes in account.

        ('See', [':func:`foo`'], ',',       'See :func:`foo`,'),
        ('See', [':func:`foo`'], '.',       'See :func:`foo`.'),
        ('See', [':func:`foo`'], ':',       'See :func:`foo`:'),
        ('See', [':func:`foo`'], ')',       'See :func:`foo`)'),
        ('See', [':func:`foo`'], ']',       'See :func:`foo`]'),
        ('See', [':func:`foo`'], ';',       'See :func:`foo`;'),
        ('See', [':func:`foo`'], '!',       'See :func:`foo`!'),
        ('See', [':func:`foo`'], '?',       'See :func:`foo`?'),
        ('See', [':func:`foo`'], '"',       'See :func:`foo`"'),
        ('See', [':func:`foo`'], "'",       "See :func:`foo`'"),
        ('See', [':func:`foo`'], '}',       'See :func:`foo`}'),

        # NOTE: whole word will have no spaces not only punctuation chars.
        ('See', [':func:`foo`'], '.)',      'See :func:`foo`.)'),
        ('See', [':func:`foo`'], '.x',      'See :func:`foo`.x'),
        ([':any:`xxx`'], '...some word',    ':any:`xxx`...some word'),

        # NOTE: but if word with punctuation has leading spaces then
        # it will be separated from boxed word.
        ([':any:`xxx`'], '  ...some word',  ':any:`xxx` ...some word'),

        # NOTE: '(', '[' are not trailing punctuation so there must be space.
        ('See', [':func:`foo`'], '(',       'See :func:`foo` ('),
        ('See', [':func:`foo`'], '[',       'See :func:`foo` ['),
    ])
    def test_oneline(self, data):
        block = WrapBlock(parent_width=128)
        for line in data[:-1]:
            if isinstance(line, list):
                block.add_boxed(line[0])
            else:
                block.add_text(line)

        pytest.g.assert_lines(list(block.get_lines()), [data[-1]])

    # Test: combined punctuations.
    def test_combined(self):
        block = WrapBlock(parent_width=128)
        block.add_text('Bla (')
        block.add_boxed(':func:`foo`')
        block.add_text(').')
        block.add_text('After test.')
        block.add_boxed('\n')
        block.add_boxed('\n')
        block.add_boxed(':any:`xxx`')
        block.add_text(', <- must be no space!')
        block.add_text('...some word')

        pytest.g.assert_lines(
            list(block.get_lines()),
            ['Bla (:func:`foo`). After test.',
             '',
             ':any:`xxx`, <- must be no space! ...some word',
             ]
        )


# Test: BlockManager.
class TestBlockManager:
    # Test: construct.
    def test_construct(self):
        m = BlockManager()
        assert m.indent == 0
        assert m.width is None
        assert m.lines == []
        assert m.block is None
        assert m._blocks == []

        m = BlockManager(indent=1, width=2)
        assert m.indent == 1
        assert m.width == 2
        assert m.lines == []
        assert m.block is None
        assert m._blocks == []

    # Test: create different types of blocks.
    def test_block_create(self):
        m = BlockManager()
        m.open_block(0, 0, 0, 0)
        assert isinstance(m.block, LineBlock)
        # If width is set then we use WrapBlock.

        m = BlockManager(width=1)
        m.open_block(0, 0, 0, 0)
        assert isinstance(m.block, WrapBlock)

        # Note: even zero width creates WrapBlock.
        m = BlockManager(width=0)
        m.open_block(0, 0, 0, 0)
        assert isinstance(m.block, WrapBlock)

        # With no_wrap we force LineBlock.
        m = BlockManager(width=1)
        m.open_block(0, 0, 0, 0, no_wrap=True)
        assert isinstance(m.block, LineBlock)

    # Test: open_block.
    def test_open_block(self):
        m = BlockManager()

        m.open_block(indent=1, first_offset=2, child_indent=7, top_margin=3,
                     bottom_margin=4)

        assert m.block is not None
        assert m.block.indent == 1
        assert m.block.first_offset == 2
        assert m.block.child_indent == 7
        assert m.block.top_margin == 3
        assert m.block.bottom_margin == 4
        assert m.block.width is None
        assert m._blocks == [m.block]

        # Clear it.
        m.clear()
        assert m.block is None
        assert m._blocks == []

        # Check if block inherits parent's list indent.
        m = BlockManager(indent=2)
        m.open_block(indent=1, first_offset=2)
        assert m.block is not None
        assert m.block.indent == 3         # indent + 2
        assert m.block.first_offset == 2

    def test_close(self):
        m = BlockManager()

        # Do nothing if not opened.
        m.close_block()

        m.open_block(indent=1, first_offset=2, top_margin=3,
                     bottom_margin=4)
        m.close_block()

        assert m.block is None

    def test_add(self):
        m = BlockManager(indent=1)
        blocks = []

        # Add one block.
        m.open_block(indent=1, top_margin=None, bottom_margin=1)
        blocks.append(m.block)

        assert m.block.indent == 2  # global indent + 1

        # Add nested block = inherit indentation.
        m.open_block(indent=1, top_margin=1, bottom_margin=1)
        assert m.block.indent == 3  # parent indent + 1

        m.close_block()
        # After closing block's parent become active.
        assert m.block == blocks[0]

        # Same level block
        m.open_block(indent=1, top_margin=1, bottom_margin=1)
        assert m.block.indent == 3  # parent indent + 1
        blocks.append(m.block)

        assert m._blocks == blocks

    def test_indent(self):
        m = BlockManager(indent=1, width=10)

        m.open_block(indent=1, top_margin=None, bottom_margin=1, child_indent=2)
        assert m.block.indent == 2  # 1 from parent + 1 explicit.
        assert m.block.width == 8

        # Inherit indent from above block since it's not closed
        # + child_indent
        m.open_block()
        assert m.block.indent == 4  # 2 from parent + 2 child_indent.
        assert m.block.width == 6
        m.close_block()

        m.close_block()

        m.open_block()
        assert m.block.indent == 1  # 1 from parent
        assert m.block.width == 9

    # Test:
    def test_text_no_wrap(self):
        m = BlockManager(indent=1)

        # Add one block.
        m.open_block(indent=1, top_margin=None, bottom_margin=1, child_indent=2)
        m.block.add_text('Lorem ipsum')
        m.block.add_text(' dolor sit amet,\nconsectetur adipiscing elit.')

        m.open_block(top_margin=0, bottom_margin=2)
        m.block.add_text('Ut enim ad minim veniam,\nquis nostrud')
        m.close_block()

        m.close_block()

        m.open_block(top_margin=0, bottom_margin=2)
        m.block.add_text('sed do eiusmod tempor\nincididunt ut labore\n')
        m.block.add_text('et dolore')
        m.close_block()

        m.open_block(indent=3, top_margin=None, bottom_margin=1)
        m.block.add_text('Duis aute irure dolor in\nreprehenderit in voluptate')
        m.close_block()

        m.close_all()

        pytest.g.assert_lines(
            m.lines,
            ['  Lorem ipsum dolor sit amet,',
             '  consectetur adipiscing elit.',
             '',
             '    Ut enim ad minim veniam,',
             '    quis nostrud',
             '',
             '',
             ' sed do eiusmod tempor',
             ' incididunt ut labore',
             ' et dolore Duis aute irure dolor in',
             '    reprehenderit in voluptate',
             ])

    # Test:
    def test_text_wrap(self):
        m = BlockManager(indent=1, width=25)

        # Add one block.
        m.open_block(indent=1, top_margin=None, bottom_margin=1, child_indent=2)
        m.block.add_text('Lorem ipsum')
        m.block.add_text(' dolor sit amet,\nconsectetur adipiscing elit.')

        m.open_block(top_margin=0, bottom_margin=2)
        m.block.add_text('Ut enim ad minim veniam,\nquis nostrud')
        m.close_block()

        m.close_block()

        m.open_block(top_margin=0, bottom_margin=2)
        m.block.add_text('sed do eiusmod tempor\nincididunt ut labore\n')
        m.block.add_text('et dolore')
        m.close_block()

        # We don't specify offset, it will be calculated based on
        # previous block's last line.
        m.open_block(indent=3, top_margin=None, bottom_margin=1)
        m.block.add_text('Duis aute irure12 in dolor\nreprehenderit in volupta')
        block = m.block
        m.close_block()

        # This method is used to prevent blank line between blocks even if
        # previous block has bottom margin.
        # We ask to merge first line and make it empty.
        m.open_block(indent=3, top_margin=None, bottom_margin=1)
        m.block.add_text('\n\n')
        m.block.add_text('----')
        m.close_block()

        # Another way is set merge_to_new_line
        m.open_block(indent=3, top_margin=None, bottom_margin=1)
        m.block.add_text('++++')
        m.block.merge_to_new_line = True
        m.close_block()

        # first_offset is calculated here.
        m.close_all()

        # first_offset = len(last line) + 1 for space - indent
        # first_offset =        6       +      1      -   3 = 4
        assert block.first_offset == 4

        pytest.g.assert_lines(
            m.lines,
            ['  Lorem ipsum dolor sit',
             '  amet, consectetur',
             '  adipiscing elit.',
             '',
             '    Ut enim ad minim',
             '    veniam, quis nostrud',
             '',
             '',
             ' sed do eiusmod tempor',
             ' incididunt ut labore et',
             ' dolore Duis aute irure12',
             '    in dolor',
             '    reprehenderit in',
             '    volupta',
             '    ----',
             '    ++++',
             ])

    def test_next_block_params(self):
        m = BlockManager(indent=1, width=25)

        # Add one block.
        m.open_block(indent=1, top_margin=None, bottom_margin=1,
                     next=dict(indent=2, bottom_margin=2))
        m.block.add_text('Lorem ipsum')
        m.block.add_text(' dolor sit amet,\nconsectetur adipiscing elit.')

        assert m._block_params == dict(indent=2, bottom_margin=2)
        m.open_block()

        assert m._block_params is None
        assert m.block.indent == 4
        m.block.add_text('Ut enim ad minim veniam,\nquis nostrud')
        m.close_block()

        m.close_block()

        m.open_block(top_margin=0, bottom_margin=2,
                     next=dict(indent=3, top_margin=None, bottom_margin=1))
        m.block.add_text('sed do eiusmod tempor\nincididunt ut labore\n')
        m.block.add_text('et dolore')
        m.close_block()

        m.open_block()
        m.block.add_text('Duis aute irure12 in dolor\nreprehenderit in volupta')
        block = m.block
        m.close_block()

        # first_offset is calculated here.
        m.close_all()

        # first_offset = len(last line) + 1 for space - indent
        # first_offset =        6       +      1      -   3 = 4
        assert block.first_offset == 4

        pytest.g.assert_lines(
            m.lines,
            ['  Lorem ipsum dolor sit',
             '  amet, consectetur',
             '  adipiscing elit.',
             '',
             '    Ut enim ad minim',
             '    veniam, quis nostrud',
             '',
             '',
             ' sed do eiusmod tempor',
             ' incididunt ut labore et',
             ' dolore Duis aute irure12',
             '    in dolor',
             '    reprehenderit in',
             '    volupta',
             ])

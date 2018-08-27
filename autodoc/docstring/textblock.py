class BaseBlock:
    def __init__(self, indent=0, first_offset=None, child_indent=0,
                 parent_width=None, top_margin=0, bottom_margin=0):
        """Construct a block.

        Args:
            indent: Block indent.
            first_offset: Extra limit for the first line
                (will be subtracted from the width).
            child_indent: Extra indent for the nested blocks.
            parent_width: Width of the parent block. This block width will be
                calculated as ``parent_width - indent``.
            top_margin: Number of blank lines before the block's content.
            bottom_margin: Number of blank lines after the block's content.
        """
        self.indent = indent
        self.first_offset = first_offset
        self.child_indent = child_indent
        self.width = parent_width - indent if parent_width else None
        self.top_margin = top_margin
        self.bottom_margin = bottom_margin
        self.merge_to_new_line = False

    def is_empty(self):
        return True

    def clear(self):
        pass

    def start_box(self):
        pass

    def end_box(self):
        pass

    def is_box_started(self):
        return False

    def add_boxed(self, text):
        raise NotImplementedError

    def add_text(self, text):
        raise NotImplementedError

    def reopen_box(self):
        raise NotImplementedError

    def get_lines(self):
        raise NotImplementedError


class LineBlock(BaseBlock):
    """Text paragraph with indentation."""
    def __init__(self, indent=0, first_offset=None, child_indent=0,
                 parent_width=None, top_margin=0, bottom_margin=0):
        super(LineBlock, self).__init__(indent, first_offset, child_indent,
                                        parent_width, top_margin, bottom_margin)
        self.clear()

    def clear(self):
        self.lines = []
        super(LineBlock, self).clear()

    def is_empty(self):
        return len(self.lines) == 0

    def add_boxed(self, text):
        self.add_text(text)

    def add_text(self, text):
        lines = text.split('\n')
        if self.lines:
            self.lines[-1] += lines[0]
            del lines[0]
        self.lines.extend(lines)

    def reopen_box(self):
        pass

    def get_lines(self):
        return iter(self.lines)


class WrapBlock(BaseBlock):
    """Text paragraph with wrapping and indentation features."""

    #: Enclosing leading (open) chars.
    enclose_start = """([{"'"""

    #: Trailing punctuation chars.
    punctuation_end = """,.:)];!?"'}"""

    def __init__(self, indent=0, first_offset=None, child_indent=0,
                 parent_width=None, top_margin=0, bottom_margin=0):
        super(WrapBlock, self).__init__(indent, first_offset, child_indent,
                                        parent_width, top_margin, bottom_margin)

        self.words = []
        self._box = None

    def clear(self):
        """Clear block."""
        self.words = []
        self._box = None
        super(WrapBlock, self).clear()

    def is_empty(self):
        return len(self.words) == 0

    def start_box(self):
        """Start block of words with disabled wrapping.

        All content added after calling the method will not be split to fit
        to the :attr:`width`.
        """
        if not self.is_box_started():
            self._box = []
            self.words.append(self._box)

    def end_box(self):
        """Close block of words with disabled wrapping."""
        if self._box:
            self._handle_enclose()
        self._box = None

    def is_box_started(self):
        return self._box is not None

    def add_boxed(self, text):
        """Add text with protecting from wrapping.

        Args:
            text: Text to add.

        Notes:
            Don't add multi line text!
        """
        if text == '\n':
            self.words.append('\n')
        else:
            self.words.append([text])
            self._handle_enclose()

    def reopen_box(self):
        """Reopen last box."""
        if self._box is None:
            self._box = self.words[-1]
            assert isinstance(self._box, list)

    def _handle_enclose(self):
        """Helper method to handle enclose chars before last box.

        It called after non-empty box is added.
        """
        # If there are at least two words and word before last is not a box
        # we check for punctuation.
        if len(self.words) > 1 and not isinstance(self.words[-2], list):
            c = self.words[-2][-1]
            if c in self.enclose_start:
                merge = True
                if c in ('"', "'"):
                    # If enclosing char occurs an even number of times in prev
                    # words then don't merge with last box.
                    #
                    # Example:
                    #
                    #   Code extracted "from pytest/setup.py" bla.
                    #
                    #   Code extracted from pytest/setup.py" bla.
                    count = 0
                    stop = len(self.words) - 2
                    for i, w in enumerate(self.words):
                        if i > stop:
                            break
                        if not isinstance(w, list):
                            count += w.count(c)
                    if count % 2 == 0:
                        merge = False

                if merge:
                    self.words[-1].insert(0, self.words[-2])
                    del self.words[-2]

    def add_text(self, text):
        """Add text to the block.

        Args:
            text: String which may contain line breaks.

        Notes:
            If :meth:`start_box` was called then text will be protected
            from the wrapping, so don't add multi line text in suc case.
        """
        # Add word to box.
        # Note: text must be without line breaks!
        if self._box is not None:
            self._box.append(text)
            return

        if not text or text == '\n':
            return
        elif text.startswith('\n'):
            text = text[1:]

        is_first_line = True
        for line in text.splitlines():
            if not line:
                words = [u'\n', u'\n']
            else:
                words = [x for x in line.strip().split(' ') if x]

            # Handle punctuation chars if prev word is boxed and given text
            # start with punctuation. Check only for very first line and word.
            #
            # It handles the following cases:
            #
            # <boxed>,text
            # <boxed>, text
            # <boxed>) text
            # <boxed>), text
            # <boxed>),text  <- in this case whole [,text] will be 'boxed'.
            # etc.
            #
            # In above cases we need to prevent spaces and line breaks
            # between boxed word and punctuation. For that we move
            # word with punctuation inside the boxed word.
            if (self.words
                    and isinstance(self.words[-1], list)
                    and is_first_line
                    and words):

                # Is first word in the text has leading space.
                # If line is empty then we force True to skip extra processing.
                leading_space = text[0].isspace() if line else True

                # If there is a space then we do nothing - in this case
                # this word will be separated by space as expected.
                # Otherwise check if word starts with punctuation char
                # add it to the boxed word.
                # NOTE: we add whole word not only punctuation chars,
                # this allows to keep original formatting.
                if not leading_space and words[0][0] in self.punctuation_end:
                    self.words[-1].append(words[0])
                    del words[0]

            self.words.extend(words)
            is_first_line = False

    def get_lines(self):
        """Get result text lines.

        Yields:
            Text lines.
        """
        # Do nothing for empty content.
        if not self.words:
            return

        line = []
        line_sz = 0
        first_word = True
        first_line = True

        for word in self.words:
            # Skip empty words and boxed lists.
            if not word:
                continue

            if first_line:
                if self.first_offset is None:
                    width = self.width
                else:
                    width = self.width - self.first_offset
            else:
                width = self.width

            # It's a protected from wrapping box of words, build result 'word'.
            if isinstance(word, list):
                word = ''.join(word)

            if word == '\n':
                word_sz = width + 1  # force new line
            else:
                word_sz = len(word) + (0 if first_word else 1)  # 1 for space

            if line_sz + word_sz <= width:
                line_sz += word_sz
                line.append(word)
                first_word = False
            else:
                # Yield empty line if it contains only offset.
                # If it's a first line and it's empty then skip it
                # (because in such case the line is not filled yet).
                if not first_line or line:
                    yield _join(line)

                if word == '\n':
                    line = []
                    line_sz = 0
                    first_word = True
                    first_line = False
                else:
                    # Recalc to have no +1 for possible space
                    # since we at line start.
                    word_sz = len(word)
                    line = [word]
                    line_sz = word_sz
                    first_line = False

        yield _join(line)


def _join(words):
    """Join words into single line.

    Args:
        words: List of words.

    Returns:
        String with space separated words.
    """
    return u' '.join(words) if words else u''


class BlockManager:
    """Blocks manager.

    It manages blocks options, indentation, merging and constructs result
    content lines.
    """

    def __init__(self, indent=0, width=None):
        """Construct manager.

        Args:
            indent: Initial indent.
            width: Content width.
        """
        self.indent = indent
        self.width = width
        self.lines = []
        self._blocks = []
        self._block_params = None
        self._last_block = None

    def clear(self):
        self._blocks = []
        self.lines = []
        self._last_block = None
        self._block_params = None

    @property
    def block(self):
        return self._blocks[-1] if self._blocks else None

    @property
    def last_width(self):
        """Last available width."""
        if self._blocks:
            return self._blocks[-1].width
        return self.width

    # NOTE: self._blocks must be non-empty
    def _dump_current_lines(self):
        block = self._blocks[-1]
        if block.is_empty():
            return

        prev_block = self._last_block

        merge = (
            (prev_block is not None and prev_block.bottom_margin is None)
            or block.top_margin is None
        )

        # Auto calculate first line offset if not specified.
        if merge and self.lines and block.first_offset is None:
            # first_offset = len(last line) + 1 for space - indent
            block.first_offset = len(self.lines[-1]) + 1 - block.indent

        lines = block.get_lines()

        # Merge with last line if prev block has None bottom margin
        # or this block has None top margin.
        #
        # There are two ways to merge starting from new line.
        # 1. Set block's merge_to_new_line=True.
        # 2. Add empty line to the top of the block content.
        #    In this case the line will be skipped on merging and
        #    remaining lines will be appended from the new line:
        #
        #        if block.width:
        #            block.add_text('\n\n')
        #        else:
        #            block.add_text('\n')
        #
        if merge and self.lines:
            # If merging is required from the new line then do nothing.
            if block.top_margin is None and block.merge_to_new_line:
                pass
            else:
                # Merge only non-empty lines.
                line = next(lines).lstrip()
                if line:
                    self.lines[-1] += u' ' + line

        # Add top margin only if there are lines.
        elif self.lines and prev_block and not block.is_empty():
            # At first make sure we have margin between blocks.
            # Choose biggest one.
            margin = max(block.top_margin, prev_block.bottom_margin)

            # Add margin between prev content and this block.
            self.lines.extend([u''] * margin)

        offset = u' ' * block.indent
        self.lines.extend(offset + x for x in lines)
        block.clear()
        self._last_block = block

    def open_block(self, indent=0, first_offset=None, child_indent=0,
                   top_margin=0, bottom_margin=0, no_wrap=False, next=None):
        """Open new block.

        If previous block is not closed then:

        * its content will be saved and block will be cleared.
        * new block inherits indentation of the previous one.

        Args:
            indent: Block indent.
            first_offset: Offset for the first line.
            child_indent: Nested blocks extra indentation.
            top_margin: Top margin (blank lines). If ``None`` then the block
                will be merged with the previous block.
            bottom_margin: Bottom margin, If ``None`` then next block will be
                merged with this one.
            no_wrap: Don't wrap content even if ``width`` is set.
            next: Arguments for the next block. Keys are the same as for this
                method. They will override parameters of the next
                :meth:`open_block` call.
        """
        if no_wrap:
            cls = LineBlock
        else:
            cls = LineBlock if self.width is None else WrapBlock

        # Add parent indent or initial one if there is no parent.
        if self._blocks:
            extra_indent = self.block.indent + self.block.child_indent
            # If existing block has content then dump it.
            self._dump_current_lines()
        else:
            extra_indent = self.indent

        if self._block_params is None:
            indent += extra_indent
            block = cls(indent=indent, first_offset=first_offset,
                        child_indent=child_indent, parent_width=self.width,
                        top_margin=top_margin, bottom_margin=bottom_margin)
        else:
            kwargs = self._block_params
            indent = kwargs.get('indent', indent) + extra_indent
            kwargs['indent'] = indent
            kwargs.setdefault('first_offset', first_offset)
            kwargs.setdefault('child_indent', child_indent)
            kwargs.setdefault('top_margin', top_margin)
            kwargs.setdefault('bottom_margin', bottom_margin)
            kwargs.setdefault('parent_width', self.width)
            block = cls(**kwargs)

        # Save next block params.
        self._block_params = next
        self._blocks.append(block)

    def close_block(self):
        """Close block."""
        if self._blocks:
            self._dump_current_lines()
            self._blocks.pop()

    def close_all(self):
        """Close all remaining blocks."""
        while self._blocks:
            self.close_block()

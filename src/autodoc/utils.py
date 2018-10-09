# Copyright 2018 Luddite Labs Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys
from itertools import zip_longest
from collections import Mapping


# TODO: improve for the following case
# Works incorrectly in situations like:
#
# """Bla bla::
#
#        some.code = 1
# """
#
# It will trim source code indentation and result will be:
#
# Bla bla::
#
# some.code = 1
#
# It's because it can't find minimum indentation value.
# The following string will be fine because last line will
# have minimum indent:
#
# """Bla bla::
#
#        some.code = 1
#
# Last line here.
# """
def trim_docstring(text, strip_leading=False, strip_trailing=False,
                   as_string=False):
    """Extended version of the ::func``trim`` from the
     https://www.python.org/dev/peps/pep-0257/.

    Strip a uniform amount of indentation from the second and further lines
    of the docstring, equal to the minimum indentation of all non-blank lines
    after the first line.

    Args:
        text: Docstring.
        strip_leading: Strip off leading blank lines.
        strip_trailing: Strip off trailing blank lines.
        as_string: Return result as string, otherwise list of lines.

    Returns:
        List of lines or string depending on ``as_string`` parameter.
    """
    if not text:
        return u'' if as_string else [u'']

    # Convert tabs to spaces (following the normal Python rules)
    # and split into a list of lines:
    if isinstance(text, list):
        lines = text
    else:
        lines = text.expandtabs().splitlines()

    # Determine minimum indentation (first line doesn't count):
    indent = sys.maxsize
    for line in lines[1:]:
        stripped = line.lstrip()
        if stripped:
            indent = min(indent, len(line) - len(stripped))

    if indent == sys.maxsize:
        indent = 0

    # Remove indentation (first line is special):
    trimmed = [lines[0].strip()]
    if indent < sys.maxsize:
        for line in lines[1:]:
            trimmed.append(line[indent:].rstrip())

    # Strip off trailing and leading blank lines:
    if strip_trailing:
        while trimmed and not trimmed[-1]:
            trimmed.pop()
    if strip_leading:
        while trimmed and not trimmed[0]:
            trimmed.pop(0)

    # Return a single string:
    if as_string:
        return u'\n'.join(trimmed)
    else:
        return trimmed


def as_lines(content):
    """This function splits given ``content`` into lines if it's a string or
    returns it as is if it's a list.

    Args:
        content: String or list of strings.

    Returns:
        List of strings.
    """
    if isinstance(content, list):
        return content
    return content.split('\n')


def get_line_indent(lines, pos):
    """Get text line indentation.

    Args:
        lines: Source code lines.
        pos: Start position to calc indentation.

    Returns:
        Next non empty indentation or ``None``.

    Note:
        ``lines`` must have text with tabs expanded.
    """
    sz = len(lines)
    while pos < sz:
        text = lines[pos]
        stripped = len(text.lstrip())
        if not stripped:
            pos += 1
            continue
        return len(text) - stripped


def get_indent(text):
    """Get text indentation.

    Args:
        text: Text to analyze.

    Returns:
        Number of leftmost spaces.

    Notes:
        Input text must be tab expanded, otherwise indent will be incorrect.
    """
    return len(text) - len(text.lstrip())


def side_by_side(left_lines, right_lines, left_text='', right_text='',
                 add_marker=True):
    """Merge lines into single list of lines to display both set of lines
    side by side.

    Args:
        left_lines: Left side lines.
        right_lines: Right side lines.
        left_text: Left side title.
        right_text: Right side title.
        add_marker: Add marker for non equal lines.

    Returns:
        Merged list of lines.
    """

    # Add header to the left side.
    # max_len - width of the 'side'.
    actual_txt = left_text
    max_len = max(len(actual_txt) + 2,
                  max(len(x) for x in left_lines) if left_lines else 0)
    lmarker = '-' * max_len
    left_lines = ([actual_txt.center(max_len, ' '), lmarker] +
                  left_lines + [lmarker])

    # Add header to the right side.
    expected_str = right_text
    rmax = max(len(expected_str) + 2,
               max(len(x) for x in right_lines) if right_lines else 0)
    rmarker = '-' * rmax
    right_lines = ([expected_str.center(rmax, ' '), rmarker] +
                   right_lines + [rmarker])

    count = max(len(left_lines), len(right_lines))

    lines = ['']
    for i, (left, right) in enumerate(zip_longest(left_lines, right_lines), -2):
        parts = [
            # Add marker if lines are different.
            '!' if add_marker and 0 <= i < count - 1 and left != right else ' ',

            # Add line number.
            # NOTE: 02 work only if there are < 100 lines.
            ' %02d | ' % i if i >= 0 else '    | ', left or '',

            # Add left line with right padding.
            ' ' * (max_len - len(left)) if left else ' ' * max_len,

            # Add content separator.
            ' | ',

            # Add right line.
            right or ''
        ]

        lines.append(''.join(parts))
    return '\n'.join(lines)


def merge_recursive(target, merge, callback=None):
    """Recursively merge given dictionaries.

    Args:
        target: Source dictionary to merge into.
        merge: Dictionary to merge into ``target``.
        callback: Callback to call on each field in the ``merge``.
    """
    if callback is None:
        def cb(*args): pass
        callback = cb

    for k, v in merge.items():
        callback(k, v)
        if (k in target and isinstance(target[k], Mapping)
                and isinstance(v, Mapping)):
            merge_recursive(target[k], v, callback)
        else:
            target[k] = v


class InheritDict:
    """This class implements immutable dictionary where nested dicts inherits
    parents' fields.

    For example::

        data = InheritDict({
            'a': 1,
            'b': True,
            'c': {'a': 2}
        })

        data['c']['a'] == 2
        data['c']['b'] is True
        data['c']['c'] is data['c']

    Lookup flow:

    * At first, a key is searching in nested dict's cache;
    * then the dict itself.
    * then in all parents in ascending direction
    * Found value is cached in the dict for faster access.

    Suppose we search field `key` in nested dict `a.b.c.d.e`, so path is
    ``a.b.c.d.e.key``. Then lookup flow will be::

        a.b.c.d.e.key
        a.b.c.d.key
        a.b.c.key
        a.b.key
        a.key
        raise KeyError

    Example::

        data = InheritDict({
            'a': 1,
            'b': True,
            'x': 2,
            'd': {
                'e': {'f': 11}
            },
            'e': {'f': 10, 'x': 18}
        })

        data['d']['e']['f'] == 11
        data['d']['e']['x'] == 2

    One more case is::

        data['d']['e']['e'] is data['d']['e']
    """
    __slots__ = ['_parent', '_name', '_data', '_cache']

    def __init__(self, data, parent=None, name=None):
        self._name = name
        self._data = data
        self._cache = {}
        self._parent = parent

        for k, v in data.items():
            if isinstance(v, dict):
                data[k] = InheritDict(v, self, k)

    def __str__(self):
        if self._name is not None:
            return '<InheritDict:%s>' % self._name
        else:
            return '<InheritDict>'

    def __getitem__(self, key):
        # At first, search in cache.
        try:
            return self._cache[key]
        except KeyError:
            pass

        # Search in this node.
        try:
            v = self._cache[key] = self._data[key]
            return v
        except KeyError:
            pass

        # Search in parents.
        parent = self._parent
        while parent:
            try:
                v = self._cache[key] = parent[key]
                return v
            except KeyError:
                pass
            parent = parent._parent

        raise KeyError(key)

    def get(self, key, default=None):
        """Get value for the given key.

        Args:
            key: Key to lookup.
            default: Default value to return if the key is not funnd.

        Returns:
            The key value or ``default``.
        """
        try:
            return self[key]
        except KeyError:
            return default

    def get_by_path(self, path):
        """Get value by dotted path.

        For example::

            data = InheritDict({'a': 1, 'b': True, 'c': {'a': 2}})
            data.get('c.a') == 2

        Args:
            path: Dotted path.

        Returns:
            Value mapped to the path.

        Raises:
            KeyError: if the path is not found.
        """
        res = self
        for name in path.split('.'):
            res = res[name]
        return res

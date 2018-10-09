# -*- coding: utf-8 -*-
"""
    sphinx.ext.napoleon.docstring
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


    Classes for docstring parsing and formatting.


    :copyright: Copyright 2007-2016 by the Sphinx team, see AUTHORS.
    :license: BSD, see LICENSE for details.

    .. note::
        This is a modified version to be used in the autodoc project.
        
        :meth:`GoogleDocstring._parse_raises_section` is changed.
        Now it generates separate :raises: field for each entry and
        also puts type inside a filed::
        
            Raises:
                ValueError: bla bla
                Other: bla bla2
                
            
            # Original
            :raises: * :exc:`ValueError` -- bla bla
                     * :exc:`Other` -- bla bla2
            
            # Our version
            :raises ValueError: bla bla
            :raises Other: bla bla2

        Modified by Sergey Kozlov <skozlovf@gmail.com>
"""

from collections.abc import Callable
import inspect
import re
from .iterators import modify_iter


_directive_regex = re.compile(r'\.\. \S+::')
_google_section_regex = re.compile(r'^(\s|\w)+:\s*$')
_google_typed_arg_regex = re.compile(r'\s*(.+?)\s*\(\s*(.*[^\s]+)\s*\)')
_numpy_section_regex = re.compile(r'^[=\-`:\'"~^_*+#<>]{2,}\s*$')
_single_colon_regex = re.compile(r'(?<!:):(?!:)')
_xref_regex = re.compile(r'(:(?:[a-zA-Z0-9]+[\-_+:.])*[a-zA-Z0-9]+:`.+?`)')
_xref_regex_g = re.compile(r'(?:[a-zA-Z0-9]+[\-_+:.])*[a-zA-Z0-9]+:`(.+?)`')
_bullet_list_regex = re.compile(r'^(\*|\+|\-)(\s+\S|\s*$)')
_enumerated_list_regex = re.compile(
    r'^(?P<paren>\()?'
    r'(\d+|#|[ivxlcdm]+|[IVXLCDM]+|[a-zA-Z])'
    r'(?(paren)\)|\.)(\s+\S|\s*$)')


class UnicodeMixin:
    """Mixin class to handle defining the proper __str__/__unicode__
    methods in Python 2 or 3."""

    def __str__(self):
        return self.__unicode__()


class GoogleDocstring(UnicodeMixin):
    """Convert Google style docstrings to reStructuredText.

    This is a modified version of the original
    :class:`sphinx.ext.napoleon.GoogleDocstring`. It adds :attr:`has_sections`
    attribute. If :attr:`has_sections` is `True` then Google style section is
    detected in the input docstring.

    Parameters
    ----------
    docstring : :obj:`str` or :obj:`list` of :obj:`str`
        The docstring to parse, given either as a string or split into
        individual lines.
    config: :obj:`sphinx.ext.napoleon.Config` or :obj:`sphinx.config.Config`
        The configuration settings to use. If not given, defaults to the
        config object on `app`; or if `app` is not given defaults to the
        a new :class:`sphinx.ext.napoleon.Config` object.


    Other Parameters
    ----------------
    app : :class:`sphinx.application.Sphinx`, optional
        Application object representing the Sphinx process.
    what : :obj:`str`, optional
        A string specifying the type of the object to which the docstring
        belongs. Valid values: "module", "class", "exception", "function",
        "method", "attribute".
    name : :obj:`str`, optional
        The fully qualified name of the object.
    obj : module, class, exception, function, method, or attribute
        The object to which the docstring belongs.
    options : :class:`sphinx.ext.autodoc.Options`, optional
        The options given to the directive: an object with attributes
        inherited_members, undoc_members, show_inheritance and noindex that
        are True if the flag option of same name was given to the auto
        directive.


    Example
    -------
    >>> from sphinx.ext.napoleon import Config
    >>> config = Config(napoleon_use_param=True, napoleon_use_rtype=True)
    >>> docstring = '''One line summary.
    ...
    ... Extended description.
    ...
    ... Args:
    ...   arg1(int): Description of `arg1`
    ...   arg2(str): Description of `arg2`
    ... Returns:
    ...   str: Description of return value.
    ... '''
    >>> print(GoogleDocstring(docstring, config))
    One line summary.
    <BLANKLINE>
    Extended description.
    <BLANKLINE>
    :param arg1: Description of `arg1`
    :type arg1: int
    :param arg2: Description of `arg2`
    :type arg2: str
    <BLANKLINE>
    :returns: Description of return value.
    :rtype: str
    <BLANKLINE>

    """
    def __init__(self, docstring, config=None, app=None, what='', name='',
                 obj=None, options=None):
        self._config = config

        assert self._config is not None

        if not what:
            if inspect.isclass(obj):
                what = 'class'
            elif inspect.ismodule(obj):
                what = 'module'
            elif isinstance(obj, Callable):
                what = 'function'
            else:
                what = 'object'

        self._what = what
        self._name = name
        self._obj = obj
        self._opt = options
        if isinstance(docstring, str):
            docstring = docstring.splitlines()
        self._lines = docstring
        self._line_iter = modify_iter(docstring, modifier=lambda s: s.rstrip())
        self._parsed_lines = []
        self._is_in_section = False
        self._section_indent = 0
        if not hasattr(self, '_directive_sections'):
            self._directive_sections = []
        if not hasattr(self, '_sections'):
            self._sections = {
                'args': self._parse_parameters_section,
                'arguments': self._parse_parameters_section,
                'attributes': self._parse_attributes_section,
                'example': self._parse_examples_section,
                'examples': self._parse_examples_section,
                'keyword args': self._parse_keyword_arguments_section,
                'keyword arguments': self._parse_keyword_arguments_section,
                'methods': self._parse_methods_section,
                'note': self._parse_note_section,
                'notes': self._parse_notes_section,
                'other parameters': self._parse_other_parameters_section,
                'parameters': self._parse_parameters_section,
                'return': self._parse_returns_section,
                'returns': self._parse_returns_section,
                'raises': self._parse_raises_section,
                'references': self._parse_references_section,
                'see also': self._parse_see_also_section,
                'todo': self._parse_todo_section,
                'warning': self._parse_warning_section,
                'warnings': self._parse_warning_section,
                'warns': self._parse_warns_section,
                'yield': self._parse_yields_section,
                'yields': self._parse_yields_section,
            }
        self.has_sections = False
        self._parse()

    def __unicode__(self):
        """Return the parsed docstring in reStructuredText format.

        Returns
        -------
        unicode
            Unicode version of the docstring.

        """
        return u'\n'.join(self.lines())

    def lines(self):
        """Return the parsed lines of the docstring in reStructuredText format.

        Returns
        -------
        list(str)
            The lines of the docstring in a list.

        """
        return self._parsed_lines

    def _consume_indented_block(self, indent=1):
        lines = []
        line = self._line_iter.peek()
        while(not self._is_section_break() and
              (not line or self._is_indented(line, indent))):
            lines.append(next(self._line_iter))
            line = self._line_iter.peek()
        return lines

    def _consume_contiguous(self):
        lines = []
        while (self._line_iter.has_next() and
               self._line_iter.peek() and
               not self._is_section_header()):
            lines.append(next(self._line_iter))
        return lines

    def _consume_empty(self):
        lines = []
        line = self._line_iter.peek()
        while self._line_iter.has_next() and not line:
            lines.append(next(self._line_iter))
            line = self._line_iter.peek()
        return lines

    def _consume_field(self, parse_type=True, prefer_type=False):
        line = next(self._line_iter)

        before, colon, after = self._partition_field_on_colon(line)
        _name, _type, _desc = before, '', after

        if parse_type:
            match = _google_typed_arg_regex.match(before)
            if match:
                _name = match.group(1)
                _type = match.group(2)

        _name = self._escape_args_and_kwargs(_name)

        if prefer_type and not _type:
            _type, _name = _name, _type
        indent = self._get_indent(line) + 1
        _desc = [_desc] + self._dedent(self._consume_indented_block(indent))
        _desc = self.__class__(_desc, self._config).lines()
        return _name, _type, _desc

    def _consume_fields(self, parse_type=True, prefer_type=False):
        self._consume_empty()
        fields = []
        while not self._is_section_break():
            _name, _type, _desc = self._consume_field(parse_type, prefer_type)
            if _name or _type or _desc:
                fields.append((_name, _type, _desc,))
        return fields

    def _consume_inline_attribute(self):
        line = next(self._line_iter)
        _type, colon, _desc = self._partition_field_on_colon(line)
        if not colon:
            _type, _desc = _desc, _type
        _desc = [_desc] + self._dedent(self._consume_to_end())
        _desc = self.__class__(_desc, self._config).lines()
        return _type, _desc

    def _consume_returns_section(self):
        lines = self._dedent(self._consume_to_next_section())
        if lines:
            before, colon, after = self._partition_field_on_colon(lines[0])
            _name, _type, _desc = '', '', lines

            if colon:
                if after:
                    _desc = [after] + lines[1:]
                else:
                    _desc = lines[1:]

                _type = before

            _desc = self.__class__(_desc, self._config).lines()
            return [(_name, _type, _desc,)]
        else:
            return []

    def _consume_usage_section(self):
        lines = self._dedent(self._consume_to_next_section())
        return lines

    def _consume_section_header(self):
        section = next(self._line_iter)
        stripped_section = section.strip(':')
        if stripped_section.lower() in self._sections:
            section = stripped_section
        return section

    def _consume_to_end(self):
        lines = []
        while self._line_iter.has_next():
            lines.append(next(self._line_iter))
        return lines

    def _consume_to_next_section(self):
        self._consume_empty()
        lines = []
        while not self._is_section_break():
            lines.append(next(self._line_iter))
        return lines + self._consume_empty()

    def _dedent(self, lines, full=False):
        if full:
            return [line.lstrip() for line in lines]
        else:
            min_indent = self._get_min_indent(lines)
            return [line[min_indent:] for line in lines]

    def _escape_args_and_kwargs(self, name):
        if name[:2] == '**':
            return r'\*\*' + name[2:]
        elif name[:1] == '*':
            return r'\*' + name[1:]
        else:
            return name

    def _fix_field_desc(self, desc):
        if self._is_list(desc):
            desc = [''] + desc
        elif desc[0].endswith('::'):
            desc_block = desc[1:]
            indent = self._get_indent(desc[0])
            block_indent = self._get_initial_indent(desc_block)
            if block_indent > indent:
                desc = [''] + desc
            else:
                desc = ['', desc[0]] + self._indent(desc_block, 4)
        return desc

    def _format_admonition(self, admonition, lines):
        lines = self._strip_empty(lines)
        if len(lines) == 1:
            return ['.. %s:: %s' % (admonition, lines[0].strip()), '']
        elif lines:
            lines = self._indent(self._dedent(lines), 3)
            return ['.. %s::' % admonition, ''] + lines + ['']
        else:
            return ['.. %s::' % admonition, '']

    def _format_block(self, prefix, lines, padding=None):
        if lines:
            if padding is None:
                padding = ' ' * len(prefix)
            result_lines = []
            for i, line in enumerate(lines):
                if i == 0:
                    result_lines.append((prefix + line).rstrip())
                elif line:
                    result_lines.append(padding + line)
                else:
                    result_lines.append('')
            return result_lines
        else:
            return [prefix]

    def _format_docutils_params(self, fields, field_role='param',
                                type_role='type'):
        lines = []
        for _name, _type, _desc in fields:
            _desc = self._strip_empty(_desc)
            if any(_desc):
                _desc = self._fix_field_desc(_desc)
                field = ':%s %s: ' % (field_role, _name)
                lines.extend(self._format_block(field, _desc))
            else:
                lines.append(':%s %s:' % (field_role, _name))

            if _type:
                lines.append(':%s %s: %s' % (type_role, _name, _type))
        return lines + ['']

    def _format_field(self, _name, _type, _desc):
        _desc = self._strip_empty(_desc)
        has_desc = any(_desc)
        separator = has_desc and ' -- ' or ''
        if _name:
            if _type:
                if '`' in _type:
                    field = '**%s** (%s)%s' % (_name, _type, separator)
                else:
                    field = '**%s** (*%s*)%s' % (_name, _type, separator)
            else:
                field = '**%s**%s' % (_name, separator)
        elif _type:
            if '`' in _type:
                field = '%s%s' % (_type, separator)
            else:
                field = '*%s*%s' % (_type, separator)
        else:
            field = ''

        if has_desc:
            _desc = self._fix_field_desc(_desc)
            if _desc[0]:
                return [field + _desc[0]] + _desc[1:]
            else:
                return [field] + _desc
        else:
            return [field]

    def _format_fields(self, field_type, fields):
        field_type = ':%s:' % field_type.strip()
        padding = ' ' * len(field_type)
        multi = len(fields) > 1
        lines = []
        for _name, _type, _desc in fields:
            field = self._format_field(_name, _type, _desc)
            if multi:
                if lines:
                    lines.extend(self._format_block(padding + ' * ', field))
                else:
                    lines.extend(self._format_block(field_type + ' * ', field))
            else:
                lines.extend(self._format_block(field_type + ' ', field))
        if lines and lines[-1]:
            lines.append('')
        return lines

    def _get_current_indent(self, peek_ahead=0):
        line = self._line_iter.peek(peek_ahead + 1)[peek_ahead]
        while line != self._line_iter.sentinel:
            if line:
                return self._get_indent(line)
            peek_ahead += 1
            line = self._line_iter.peek(peek_ahead + 1)[peek_ahead]
        return 0

    def _get_indent(self, line):
        for i, s in enumerate(line):
            if not s.isspace():
                return i
        return len(line)

    def _get_initial_indent(self, lines):
        for line in lines:
            if line:
                return self._get_indent(line)
        return 0

    def _get_min_indent(self, lines):
        min_indent = None
        for line in lines:
            if line:
                indent = self._get_indent(line)
                if min_indent is None:
                    min_indent = indent
                elif indent < min_indent:
                    min_indent = indent
        return min_indent or 0

    def _indent(self, lines, n=4):
        return [((' ' * n) + line) if line else '' for line in lines]

    def _is_indented(self, line, indent=1):
        for i, s in enumerate(line):
            if i >= indent:
                return True
            elif not s.isspace():
                return False
        return False

    def _is_list(self, lines):
        if not lines:
            return False
        if _bullet_list_regex.match(lines[0]):
            return True
        if _enumerated_list_regex.match(lines[0]):
            return True
        if len(lines) < 2 or lines[0].endswith('::'):
            return False
        indent = self._get_indent(lines[0])
        next_indent = indent
        for line in lines[1:]:
            if line:
                next_indent = self._get_indent(line)
                break
        return next_indent > indent

    def _is_section_header(self):
        section = self._line_iter.peek().lower()
        match = _google_section_regex.match(section)
        if match and section.strip(':') in self._sections:
            header_indent = self._get_indent(section)
            section_indent = self._get_current_indent(peek_ahead=1)
            return section_indent > header_indent
        elif self._directive_sections:
            if _directive_regex.match(section):
                for directive_section in self._directive_sections:
                    if section.startswith(directive_section):
                        return True
        return False

    def _is_section_break(self):
        line = self._line_iter.peek()
        return (not self._line_iter.has_next() or
                self._is_section_header() or
                (self._is_in_section and
                    line and
                    not self._is_indented(line, self._section_indent)))

    def _parse(self):
        self._parsed_lines = self._consume_empty()

        if self._name and (self._what == 'attribute' or self._what == 'data'):
            self._parsed_lines.extend(self._parse_attribute_docstring())
            return

        while self._line_iter.has_next():
            if self._is_section_header():
                try:
                    section = self._consume_section_header()
                    self._is_in_section = True
                    self._section_indent = self._get_current_indent()
                    if _directive_regex.match(section):
                        lines = [section] + self._consume_to_next_section()
                    else:
                        lines = self._sections[section.lower()](section)
                    # Set flag is Google style section is found.
                    self.has_sections = True
                finally:
                    self._is_in_section = False
                    self._section_indent = 0
            else:
                if not self._parsed_lines:
                    lines = self._consume_contiguous() + self._consume_empty()
                else:
                    lines = self._consume_to_next_section()
            self._parsed_lines.extend(lines)

    def _parse_attribute_docstring(self):
        _type, _desc = self._consume_inline_attribute()
        return self._format_field('', _type, _desc)

    def _parse_attributes_section(self, section):
        lines = []
        for _name, _type, _desc in self._consume_fields():
            if self._config.napoleon_use_ivar:
                field = ':ivar %s: ' % _name
                lines.extend(self._format_block(field, _desc))
                if _type:
                    lines.append(':vartype %s: %s' % (_name, _type))
            else:
                lines.extend(['.. attribute:: ' + _name, ''])
                field = self._format_field('', _type, _desc)
                lines.extend(self._indent(field, 3))
                lines.append('')
        if self._config.napoleon_use_ivar:
            lines.append('')
        return lines

    def _parse_examples_section(self, section):
        use_admonition = self._config.napoleon_use_admonition_for_examples
        return self._parse_generic_section(section, use_admonition)

    def _parse_usage_section(self, section):
        header = ['.. rubric:: Usage:', '']
        block = ['.. code-block:: python', '']
        lines = self._consume_usage_section()
        lines = self._indent(lines, 3)
        return header + block + lines + ['']

    def _parse_generic_section(self, section, use_admonition):
        lines = self._strip_empty(self._consume_to_next_section())
        lines = self._dedent(lines)
        if use_admonition:
            header = '.. admonition:: %s' % section
            lines = self._indent(lines, 3)
        else:
            header = '.. rubric:: %s' % section
        if lines:
            return [header, ''] + lines + ['']
        else:
            return [header, '']

    def _parse_keyword_arguments_section(self, section):
        fields = self._consume_fields()
        if self._config.napoleon_use_keyword:
            return self._format_docutils_params(
                fields,
                field_role="keyword",
                type_role="kwtype")
        else:
            return self._format_fields('Keyword Arguments', fields)

    def _parse_methods_section(self, section):
        lines = []
        for _name, _, _desc in self._consume_fields(parse_type=False):
            lines.append('.. method:: %s' % _name)
            if _desc:
                lines.extend([''] + self._indent(_desc, 3))
            lines.append('')
        return lines

    def _parse_note_section(self, section):
        lines = self._consume_to_next_section()
        return self._format_admonition('note', lines)

    def _parse_notes_section(self, section):
        use_admonition = self._config.napoleon_use_admonition_for_notes
        return self._parse_generic_section('Notes', use_admonition)

    def _parse_other_parameters_section(self, section):
        return self._format_fields('Other Parameters', self._consume_fields())

    def _parse_parameters_section(self, section):
        fields = self._consume_fields()
        if self._config.napoleon_use_param:
            return self._format_docutils_params(fields)
        else:
            return self._format_fields('Parameters', fields)

    def _parse_raises_section(self, section):
        fields = self._consume_fields(parse_type=False, prefer_type=True)
        lines = []

        for _, _type, _desc in fields:
            _desc = self._strip_empty(_desc)
            has_desc = any(_desc)
            first_desc = None
            tag = None

            if _type.startswith(r'\* '):
                _type = _type[3:]

            if _type:
                has_refs = '`' in _type or ':' in _type
                has_space = any(c in ' \t\n\v\f ' for c in _type)

                if not has_refs and not has_space:
                    tag = ':raises %s:' % _type
                elif has_refs and not has_space:
                    # Get name from :<tag>:`<name>`
                    m = _xref_regex_g.search(_type)
                    if m:
                        tag = ':raises %s:' % m.group(1)
                    else:
                        first_desc = '%s ' % _type
                elif has_desc:
                    if has_space and not has_refs:
                        first_desc = '*%s* -- ' % _type
                    else:
                        first_desc = '%s ' % _type
                else:
                    _desc = [_type]

            if first_desc:
                _desc.insert(0, first_desc)

            tag = tag or ':raises:'
            postfix = ' ' if _desc else ''
            lines.extend(self._format_block(tag + postfix, _desc))

        if lines and lines[-1]:
            lines.append('')
        return lines

    def _parse_references_section(self, section):
        use_admonition = self._config.napoleon_use_admonition_for_references
        return self._parse_generic_section('References', use_admonition)

    def _parse_returns_section(self, section):
        fields = self._consume_returns_section()
        multi = len(fields) > 1
        if multi:
            use_rtype = False
        else:
            use_rtype = self._config.napoleon_use_rtype

        lines = []
        for _name, _type, _desc in fields:
            if use_rtype:
                field = self._format_field(_name, '', _desc)
            else:
                field = self._format_field(_name, _type, _desc)

            if multi:
                if lines:
                    lines.extend(self._format_block('          * ', field))
                else:
                    lines.extend(self._format_block(':returns: * ', field))
            else:
                lines.extend(self._format_block(':returns: ', field))
                if _type and use_rtype:
                    lines.extend([':rtype: %s' % _type, ''])
        if lines and lines[-1]:
            lines.append('')
        return lines

    def _parse_see_also_section(self, section):
        lines = self._consume_to_next_section()
        return self._format_admonition('seealso', lines)

    def _parse_todo_section(self, section):
        lines = self._consume_to_next_section()
        return self._format_admonition('todo', lines)

    def _parse_warning_section(self, section):
        lines = self._consume_to_next_section()
        return self._format_admonition('warning', lines)

    def _parse_warns_section(self, section):
        return self._format_fields('Warns', self._consume_fields())

    def _parse_yields_section(self, section):
        fields = self._consume_returns_section()
        return self._format_fields('Yields', fields)

    def _partition_field_on_colon(self, line):
        before_colon = []
        after_colon = []
        colon = ''
        found_colon = False
        for i, source in enumerate(_xref_regex.split(line)):
            if found_colon:
                after_colon.append(source)
            else:
                m = _single_colon_regex.search(source)
                if (i % 2) == 0 and m:
                    found_colon = True
                    colon = source[m.start(): m.end()]
                    before_colon.append(source[:m.start()])
                    after_colon.append(source[m.end():])
                else:
                    before_colon.append(source)

        return ("".join(before_colon).strip(),
                colon,
                "".join(after_colon).strip())

    def _strip_empty(self, lines):
        if lines:
            start = -1
            for i, line in enumerate(lines):
                if line:
                    start = i
                    break
            if start == -1:
                lines = []
            end = -1
            for i in reversed(list(range(len(lines)))):
                line = lines[i]
                if line:
                    end = i
                    break
            if start > 0 or end + 1 < len(lines):
                lines = lines[start:end + 1]
        return lines


class NumpyDocstring(GoogleDocstring):
    """Convert NumPy style docstrings to reStructuredText.

    This is a modified version of the original
    :class:`sphinx.ext.napoleon.NumpyDocstring`. It adds :attr:`has_sections`
    attribute. If :attr:`has_sections` is `True` then NumPy style section is
    detected in the input docstring.

    Parameters
    ----------
    docstring : :obj:`str` or :obj:`list` of :obj:`str`
        The docstring to parse, given either as a string or split into
        individual lines.
    config: :obj:`sphinx.ext.napoleon.Config` or :obj:`sphinx.config.Config`
        The configuration settings to use. If not given, defaults to the
        config object on `app`; or if `app` is not given defaults to the
        a new :class:`sphinx.ext.napoleon.Config` object.


    Other Parameters
    ----------------
    app : :class:`sphinx.application.Sphinx`, optional
        Application object representing the Sphinx process.
    what : :obj:`str`, optional
        A string specifying the type of the object to which the docstring
        belongs. Valid values: "module", "class", "exception", "function",
        "method", "attribute".
    name : :obj:`str`, optional
        The fully qualified name of the object.
    obj : module, class, exception, function, method, or attribute
        The object to which the docstring belongs.
    options : :class:`sphinx.ext.autodoc.Options`, optional
        The options given to the directive: an object with attributes
        inherited_members, undoc_members, show_inheritance and noindex that
        are True if the flag option of same name was given to the auto
        directive.


    Example
    -------
    >>> from sphinx.ext.napoleon import Config
    >>> config = Config(napoleon_use_param=True, napoleon_use_rtype=True)
    >>> docstring = '''One line summary.
    ...
    ... Extended description.
    ...
    ... Parameters
    ... ----------
    ... arg1 : int
    ...     Description of `arg1`
    ... arg2 : str
    ...     Description of `arg2`
    ... Returns
    ... -------
    ... str
    ...     Description of return value.
    ... '''
    >>> print(NumpyDocstring(docstring, config))
    One line summary.
    <BLANKLINE>
    Extended description.
    <BLANKLINE>
    :param arg1: Description of `arg1`
    :type arg1: int
    :param arg2: Description of `arg2`
    :type arg2: str
    <BLANKLINE>
    :returns: Description of return value.
    :rtype: str
    <BLANKLINE>

    Methods
    -------
    __str__()
        Return the parsed docstring in reStructuredText format.

        Returns
        -------
        str
            UTF-8 encoded version of the docstring.

    __unicode__()
        Return the parsed docstring in reStructuredText format.

        Returns
        -------
        unicode
            Unicode version of the docstring.

    lines()
        Return the parsed lines of the docstring in reStructuredText format.

        Returns
        -------
        list(str)
            The lines of the docstring in a list.

    """
    def __init__(self, docstring, config=None, app=None, what='', name='',
                 obj=None, options=None):
        self._directive_sections = ['.. index::']
        super(NumpyDocstring, self).__init__(docstring, config, app, what,
                                             name, obj, options)

    def _consume_field(self, parse_type=True, prefer_type=False):
        line = next(self._line_iter)
        if parse_type:
            _name, _, _type = self._partition_field_on_colon(line)
        else:
            _name, _type = line, ''
        _name, _type = _name.strip(), _type.strip()
        _name = self._escape_args_and_kwargs(_name)

        if prefer_type and not _type:
            _type, _name = _name, _type
        indent = self._get_indent(line) + 1
        _desc = self._dedent(self._consume_indented_block(indent))
        _desc = self.__class__(_desc, self._config).lines()
        return _name, _type, _desc

    def _consume_returns_section(self):
        return self._consume_fields(prefer_type=True)

    def _consume_section_header(self):
        section = next(self._line_iter)
        if not _directive_regex.match(section):
            # Consume the header underline
            next(self._line_iter)
        return section

    def _is_section_break(self):
        line1, line2 = self._line_iter.peek(2)
        return (not self._line_iter.has_next() or
                self._is_section_header() or
                ['', ''] == [line1, line2] or
                (self._is_in_section and
                    line1 and
                    not self._is_indented(line1, self._section_indent)))

    def _is_section_header(self):
        section, underline = self._line_iter.peek(2)
        section = section.lower()
        if section in self._sections and isinstance(underline, str):
            return bool(_numpy_section_regex.match(underline))
        elif self._directive_sections:
            if _directive_regex.match(section):
                for directive_section in self._directive_sections:
                    if section.startswith(directive_section):
                        return True
        return False

    _name_rgx = re.compile(r"^\s*(:(?P<role>\w+):`(?P<name>[a-zA-Z0-9_.-]+)`|"
                           r" (?P<name2>[a-zA-Z0-9_.-]+))\s*", re.X)

    def _parse_see_also_section(self, section):
        lines = self._consume_to_next_section()
        try:
            return self._parse_numpydoc_see_also_section(lines)
        except ValueError:
            return self._format_admonition('seealso', lines)

    def _parse_numpydoc_see_also_section(self, content):
        """
        Derived from the NumpyDoc implementation of _parse_see_also.

        See Also
        --------
        func_name : Descriptive text
            continued text
        another_func_name : Descriptive text
        func_name1, func_name2, :meth:`func_name`, func_name3

        """
        items = []

        def parse_item_name(text):
            """Match ':role:`name`' or 'name'"""
            m = self._name_rgx.match(text)
            if m:
                g = m.groups()
                if g[1] is None:
                    return g[3], None
                else:
                    return g[2], g[1]
            raise ValueError("%s is not a item name" % text)

        def push_item(name, rest):
            if not name:
                return
            name, role = parse_item_name(name)
            items.append((name, list(rest), role))
            del rest[:]

        current_func = None
        rest = []

        for line in content:
            if not line.strip():
                continue

            m = self._name_rgx.match(line)
            if m and line[m.end():].strip().startswith(':'):
                push_item(current_func, rest)
                current_func, line = line[:m.end()], line[m.end():]
                rest = [line.split(':', 1)[1].strip()]
                if not rest[0]:
                    rest = []
            elif not line.startswith(' '):
                push_item(current_func, rest)
                current_func = None
                if ',' in line:
                    for func in line.split(','):
                        if func.strip():
                            push_item(func, [])
                elif line.strip():
                    current_func = line
            elif current_func is not None:
                rest.append(line.strip())
        push_item(current_func, rest)

        if not items:
            return []

        roles = {
            'method': 'meth',
            'meth': 'meth',
            'function': 'func',
            'func': 'func',
            'class': 'class',
            'exception': 'exc',
            'exc': 'exc',
            'object': 'obj',
            'obj': 'obj',
            'module': 'mod',
            'mod': 'mod',
            'data': 'data',
            'constant': 'const',
            'const': 'const',
            'attribute': 'attr',
            'attr': 'attr'
        }
        if self._what is None:
            func_role = 'obj'
        else:
            func_role = roles.get(self._what, '')
        lines = []
        last_had_desc = True
        for func, desc, role in items:
            if role:
                link = ':%s:`%s`' % (role, func)
            elif func_role:
                link = ':%s:`%s`' % (func_role, func)
            else:
                link = "`%s`_" % func
            if desc or last_had_desc:
                lines += ['']
                lines += [link]
            else:
                lines[-1] += ", %s" % link
            if desc:
                lines += self._indent([' '.join(desc)])
                last_had_desc = True
            else:
                last_had_desc = False
        lines += ['']

        return self._format_admonition('seealso', lines)

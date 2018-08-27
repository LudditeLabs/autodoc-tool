"""
This module provides unknown (non-registered) directives support.

It injects a hook to the docutils workflow by replacing
:func:`docutils.parsers.rst.directives.directive` and
returns :class:`UnknownDirective` handler if no other handler is found.

:class:`UnknownDirective` creates special document node
:class:`autodoc_unknown_directive` which is handled by the
:class:`CommonTranslator`.
"""
from docutils.parsers.rst import nodes, directives, Directive
from docutils.parsers.rst.directives.admonitions import BaseAdmonition
from .nodes import seealso, todo

# List of known but not registered directives.
# They are from the Sphinx.
# http://www.sphinx-doc.org/en/stable/markup/para.html
# http://www.sphinx-doc.org/en/stable/markup/misc.html
known_directives = ['versionadded', 'versionchanged', 'deprecated',
                    'rubric', 'centered', 'hlist', 'glossary', 'productionlist',
                    'highlight', 'code-block', 'literalinclude',
                    'sectionauthor', 'codeauthor', 'index', 'only',
                    'tabularcolumns']


class autodoc_unknown_directive(nodes.Element):
    #: List of params.
    params = None

    #: If ``True`` then directive has content on the same line.
    first_line_content = False


# TODO: substitutions are not supported.
# Like ``.. |bla| name:: ...``
# Because to parse substitution we have to provide :attr:`option_spec`.
# But we don't know directive options. As a workaround we can
# set :attr:`optional_arguments` to MAXSIZE, but the all content will be
# parsed as directive parameters. So we just don't parse directive options.
class UnknownDirective(Directive):
    """Unknown directive handler."""
    has_content = True
    final_argument_whitespace = True

    def run(self):
        node = autodoc_unknown_directive(self.block_text, **self.options)
        node.tagname = self.name
        node.source, node.line = (
            self.state_machine.get_source_and_line(self.lineno))
        # Is something placed on the same line as directive?
        try:
            first = self.block_text[:self.block_text.index('\n')].strip()
        except ValueError:
            first = self.block_text.strip()
        node.first_line_content = not first.endswith('::')

        pos = None
        first_colon_pos = None
        content = None

        # Separate parameters from content.
        for i, line in enumerate(self.content):
            if first_colon_pos is None and line.startswith(':'):
                first_colon_pos = i
            if not line:
                pos = i
                break

        if self.content:
            # If content has no fields ':bla:' then we put everything as
            # directive content.
            if first_colon_pos is None:
                if node.first_line_content:
                    node.params = self.content[0:1]
                    content = self.content[1:]
                else:
                    content = self.content
            # If there is a blank line then everything above it are params,
            # below - directive content.
            elif pos is not None:
                node.params = self.content[:pos]
                content = self.content[pos + 1:]
            # In all other cases assume everything is params.
            else:
                node.params = self.content

        # Parse content if exists.
        if content is not None:
            self.state.nested_parse(content, self.content_offset, node)
        return [node]


class SeeAlsoDirective(BaseAdmonition):
    node_class = seealso


class TodoDirective(BaseAdmonition):
    node_class = todo


def directive_hook(directive_name, language_module, document):
    directive, messages = directive_hook.orig(directive_name, language_module,
                                              document)
    return directive or UnknownDirective, messages


def register_directives():
    directives.register_directive('seealso', SeeAlsoDirective)
    directives.register_directive('todo', TodoDirective)
    for name in known_directives:
        directives.register_directive(name, UnknownDirective)


def set_directive_hook():
    registered = hasattr(directive_hook, 'orig')
    if not registered:
        directive_hook.orig = directives.directive
        directives.directive = directive_hook
    return registered


def init():
    already_init = set_directive_hook()
    if not already_init:
        register_directives()

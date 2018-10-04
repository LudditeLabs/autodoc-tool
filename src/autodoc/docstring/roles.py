"""
This module provides unknown (non-registered) roles support.

It injects a hook to the docutils workflow by replacing
:func:`docutils.parsers.rst.roles.role` and returns
:func:`common_role` handler if no role is found.

:func:`common_role` creates special document node :class:`autodoc_unknown_role`
which is handled by the :class:`CommonTranslator`.
"""
from docutils.parsers.rst import nodes, roles

# List of known but not registered roles.
# They are from the Sphinx.
# http://www.sphinx-doc.org/en/stable/markup/inline.html
# sphinx/roles.py
known_roles = ['any', 'download', 'doc', 'guilabel', 'menuselection',
               'file', 'samp', 'abbr', 'index', 'command', 'dfn',
               'kbd', 'mailheader', 'makevar', 'manpage', 'mimetype',
               'newsgroup', 'program', 'regexp', 'ref', 'numref',
               'envvar', 'token', 'keyword', 'option', 'term',
               'index', 'attr', 'attribute', 'class', 'meth', 'method', 'obj',
               'func', 'exc', 'mod']


class autodoc_unknown_role(nodes.Inline, nodes.TextElement):
    """Unknown role node."""
    pass


def common_role(role, rawtext, text, lineno, inliner, options=None,
                content=None):
    """Unknown role handler.

    It used to have a test node in the document.
    """
    options = options if options is not None else {}
    roles.set_classes(options)
    options['attributes'] = {'text': text}
    node = autodoc_unknown_role(rawtext, rawtext, **options)
    node.role_name = role
    node.source, node.line = inliner.reporter.get_source_and_line(lineno)
    return [node], []


# This role is applied to interpreted text without a role: `text`.
def default_role(role, rawtext, *args, **kwargs):
    """Default role to return raw text node."""
    # return [nodes.Text(rawtext)], []
    text = rawtext.strip('`')
    return [nodes.emphasis(text, text, default_role=True)], []


def register_roles():
    for name in known_roles:
        roles.register_local_role(name, common_role)


def set_default_role():
    """Set custom default role.

    By default::

        `text` -> :title:`text`

    we override with our role::

        `text` -> `text`

    See Also:
        :attr:`roles.DEFAULT_INTERPRETED_ROLE`.
    """
    if roles._roles.get('') != default_role:
        roles._roles[''] = default_role


def role_hook(role_name, language_module, lineno, reporter):
    """Hook to provide common role if nothing is found."""
    role_fn, messages = role_hook.orig(role_name, language_module, lineno,
                                       reporter)
    return role_fn or common_role, messages


def set_role_hook():
    """Replace :func:`roles.role` with custom function.

    It returns common role node for all nonexistent roles.
    """
    registered = hasattr(role_hook, 'orig')
    if not registered:
        role_hook.orig = roles.role
        roles.role = role_hook
    return registered


def init():
    already_init = set_role_hook()
    if not already_init:
        set_default_role()
        register_roles()

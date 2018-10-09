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

"""
Inline markup
-------------

This module implements inline markup and roles.

Common markup:

    *emphasis*
    **strong emphasis**
    `interpreted text`
    ``inline literals``

References:

    standalone hyperlinks (http://www.python.org)
    external hyperlinks (Python_)
    internal cross-references (example_)
    footnote references ([1]_) - not supported yet
    citation references ([CIT2002]_)  - not supported yet
    substitution references (|example|, |refname|_, |refname|__)
    and _`inline internal targets`.
    :pep-reference:, :PEP:
    :rfc-reference:, :RFC:
    targets (.. _target:: <uri>)

Roles:

    :subscript:, :sub:
    :superscript:, :sup:
    :title-reference:, :t:, :title:
    :math:
"""
from docutils import nodes
from ....docstring.utils import get_role_part, get_target_name


# TODO: not implemented roles
# (See from docutils.parsers.rst.roles._role_registry):
# code - special role...
# raw - special role...
# abbreviation - what is it?
#
# unimplemented_role:
# index
# named-reference
# anonymous-reference
# uri-reference
# footnote-reference
# citation-reference
# substitution-reference
# target
# restructuredtext-unimplemented-role
# TODO: handle raw role.
# http://docutils.sourceforge.net/docs/ref/rst/roles.html#specialized-roles
class InlineMixin:
    def short_or_long(self, node, short, long=None):
        """Aux method to add short or long version of the inline markup.

        If text starts with ``:`` then it's a long version of the rule.
        For such roles we use shorten version if ``shorten_inline`` option
        is ``True``. Otherwise keep original.

        For short rules always use ``short``.

        Args:
            node: Current node.
            short: Text for short version.
            long: Text for long version. If ``None`` then first part of the
                role will be used.
        """
        is_short = not node.rawsource.startswith(':')
        if is_short or self.options['shorten_inline']:
            self.block.add_text(short)
        else:
            self.block.add_text(get_role_part(node.rawsource) if long is None
                                else long)

    def add_inline_role(self, node, role_part=None, short=None, long=None):
        """Helper method to add inline role.

        It adds role as a protected from wrapping text box.

        Args:
            node: Role node.
            role_part: Inline role prefix::

                    :role:`

                If not set, then auto detected.
            short: Short role version.
            long: Long role version.

        See Also:
            :func:`_get_role_part`, :meth:`short_or_long`.
        """
        self.block.start_box()
        if short is not None:
            self.short_or_long(node, short, long=long)
            if role_part is None:
                role_part = get_role_part(node.rawsource)
            self.block.add_text(node.rawsource[len(role_part):])
        self.block.end_box()

    # :emphasis:`text`, *text*
    def visit_emphasis(self, node):
        self.block.start_box()
        short = '`' if node.get('default_role') else '*'
        self.short_or_long(node, short=short)

    def depart_emphasis(self, node):
        short = '`' if node.get('default_role') else '*'
        self.short_or_long(node, short=short, long=u'`')
        self.block.end_box()

    # :strong:`text`, **text**
    def visit_strong(self, node):
        self.block.start_box()
        self.short_or_long(node, short=u'**')

    def depart_strong(self, node):
        self.short_or_long(node, short=u'**', long=u'`')
        self.block.end_box()

    # :literal:`text`, ``text``
    # TODO: check for backslashes.
    def visit_literal(self, node):
        self.block.start_box()
        is_long = node.rawsource.startswith(':')
        # http://docutils.sourceforge.net/docs/ref/rst/roles.html#literal:
        #
        #     ``text \ and \ backslashes``
        #     :literal:`text \ and \ backslashes`
        #
        #     The backslashes in the first line are preserved (and do nothing),
        #     whereas the backslashes in the second line escape
        #     the following spaces.
        #
        # Don't shorten long version if there are backslashes since this
        # changes parsing behaviour.
        if is_long and '\\' in node.rawsource:
            part = get_role_part(node.rawsource)
            # If it's a :literal:` ... \ ` with backslashes then they will be
            # removed while document building so we replace original Text node
            # with own where preserve backslashes.
            node.children[0] = nodes.Text(node.rawsource[len(part):-1])
            self.block.add_text(part)
        else:
            self.short_or_long(node, short=u'``')

    def depart_literal(self, node):
        is_long = node.rawsource.startswith(':')
        if is_long and '\\' in node.rawsource:
            self.block.add_text(u'`')
        else:
            self.short_or_long(node, short=u'``', long=u'`')
        self.block.end_box()

    # :subscript:, :sub:
    def visit_subscript(self, node):
        self.block.start_box()
        self.short_or_long(node, short=u':sub:`')

    def depart_subscript(self, node):
        self.block.add_text(u'`')
        self.block.end_box()

    # :superscript:, :sup:
    def visit_superscript(self, node):
        self.block.start_box()
        self.short_or_long(node, short=u':sup:`')

    def depart_superscript(self, node):
        self.block.add_text(u'`')
        self.block.end_box()

    # :title-reference:, :t:, :title:
    def visit_title_reference(self, node):
        self.block.start_box()
        self.short_or_long(node, short=u':t:`')

    def depart_title_reference(self, node):
        self.block.add_text(u'`')
        self.block.end_box()

    # :math:`latex math`
    def visit_math(self, node):
        self.block.start_box()
        self.block.add_text(u':math:`')

    def depart_math(self, node):
        self.block.add_text(u'`')
        self.block.end_box()

    # References.
    #
    #     :PEP:, :RFC:, http://blalb, mailto:bla@bla, |substitution|,
    #     |substitution|_, |substitution|__, `A HYPERLINK`_
    #
    # http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html#substitution-references
    # http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html#standalone-hyperlinks
    #
    # Complex case is a hyperlink reference with embedded URIs and aliases:
    #
    # `ITER <https://docs.python.org>`_
    # <reference name="ITER" refuri="https://python.org">ITER</reference>
    # <target ids="['iter']" names="[u'iter']" refuri="https://python.org"/>
    #
    # `link <Python home page_>`_
    # <reference name="link" refname="python home page">link</reference>
    # <target names="[u'link']" refname="python home page"/>
    #
    # In such case target node must be skipped from rendering.
    def visit_reference(self, node):
        def get_target():
            i = node.parent.children.index(node) + 1
            if i < len(node.parent):
                next_sibling = node.parent.children[i]
                if isinstance(next_sibling, nodes.target):
                    return next_sibling

        rawsource = node.rawsource
        name = node.get('name')
        refuri = node.get('refuri')
        refname = node.get('refname')

        # Handle `text <ref>`_ construction, see complex case comments above.
        if name:
            if refname:
                target = get_target()
                if target and target.get('refname') == refname:
                    target['skip'] = 1
            if refuri:
                target = get_target()
                if target and target.get('refuri') == refuri:
                    target['skip'] = 1

        # :pep-reference:, :PEP:
        elif rawsource.startswith(u':pep'):
            part = get_role_part(node.rawsource)
            self.add_inline_role(node, part, short=u':PEP:`')
            raise nodes.SkipNode

        # :rfc-reference:, :RFC:
        elif rawsource.startswith(':rfc'):
            part = get_role_part(node.rawsource)
            self.add_inline_role(node, part, short=u':RFC:`')
            raise nodes.SkipNode

        if '\n' in rawsource:
            self.block.add_text(rawsource)
        else:
            self.block.add_boxed(rawsource)
        raise nodes.SkipNode

    def depart_reference(self, node):
        pass

    # |subs|, |subs|_, |subs|__
    # Last two is wrapped with reference node.
    def visit_substitution_reference(self, node):
        txt = u'|{}|'.format(node['refname'])
        if self.block.is_box_started():
            self.block.add_text(txt)
        else:
            self.block.add_boxed(txt)
        raise nodes.SkipNode

    def depart_substitution_reference(self, node):
        pass

    # Targets.
    #
    # http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html#hyperlink-targets

    def visit_target(self, node):
        # This attr is set by visit_reference() for hyperlink reference
        # with embedded URIs and aliases.
        if node.get('skip') == 1:
            raise nodes.SkipNode

        if node.children:
            self.block.start_box()
            self.block.add_text(u'_`')
        else:
            #
            # .. _target::
            #
            # <paragraph>
            #
            # For multiline targets we add 1 line margin:
            #
            #     .. _starts-on-this-line: http://
            #     docutils.sourceforge.net/rst.html
            #
            #     .. _entirely-below:
            #     http://docutils.
            #     sourceforge.net/rst.html
            #
            name = get_target_name(node)
            self.open_block(top_margin=0, bottom_margin=0)
            if 'refuri' in node:
                refuri_ = node['refuri']
            else:
                refuri_ = node.rawsource[node.rawsource.index(':')+2:]
            self.block.add_boxed(u'.. _{}: {}'.format(name, refuri_))
            self.close_block()

    def depart_target(self, node):
        if node.children:
            self.block.add_text(u'`')
            self.block.end_box()

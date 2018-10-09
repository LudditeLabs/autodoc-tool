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

from collections import OrderedDict
from itertools import chain
from .base import DocumentTransform
from ..nodes import docstring_section


class CollectSectionsBase(DocumentTransform):
    """Base class to implement sections collectors.

    Subclass needs to implement :meth:`get_handler_name` and
    ``process_<name>`` methods to process specific nodes.
    """

    #: Mapping of the aliases to the handler name.
    #:
    #: Example::
    #:
    #:     handler_aliases = dict(one=two, ones=two)
    #:
    handler_aliases = None

    def __init__(self, *args, **kwargs):
        super(CollectSectionsBase, self).__init__(*args, **kwargs)
        self._to_remove = None

    def set_handler_aliases(self, name, aliases):
        """Set handler aliases.

        Args:
            name: Handler name (without a ``process_`` prefix).
            aliases: List of aliases.
        """
        if self.handler_aliases is None:
            self.handler_aliases = {}
        for v in aliases:
            self.handler_aliases[v] = name

    def get_docstring_section(self, name, first_node=None):
        """Get or create a section.

        Args:
            name: Section name.
            first_node: Original node which triggers section building.

        See Also:
            :class:`docstring_section`.
        """
        sections = self.document.field_sections
        section = sections.get(name)
        if section is None and first_node is not None:
            section = docstring_section(name, first_node)
            sections[name] = section
        return section

    def add_to_remove(self, node):
        """Add the node to be removed after document processing.

        Args:
            node: Document node to remove.

        See Also:
            :meth:`do_remove_nodes`.
        """
        if self._to_remove is None:
            self._to_remove = {node}
        else:
            self._to_remove.add(node)

    def do_remove_nodes(self):
        """Remove nodes added to be removed.

        It also removes node's parent if the parent is empty.
        """
        if self._to_remove is not None:
            for node in self._to_remove:
                parent = node.get('real_parent', node.parent)
                node.delattr('real_parent')
                parent.remove(node)
                if not len(parent):
                    parent.parent.remove(parent)
            self._to_remove = None

    def call_handler(self, name, node, **kwargs):
        """Call handler by name.

        This method calls method `process_<name>(node)` if it implemented.

        Args:
            name: Handler name or alias.
            node: Node to pass to the handler.
            kwargs: Keyword arguments to pass to the handler.

        Returns:
            ``True`` if handler is found, ``False`` otherwise.

        See Also:
            :meth:`get_handler_name`.
        """
        name = name.lower()
        if self.handler_aliases:
            name = self.handler_aliases.get(name, name)
        h = getattr(self, 'process_' + name, None)
        if h:
            # This attr will be used to remove the node.
            node['real_parent'] = node.parent
            h(node, **kwargs)
            return True
        return False

    def get_handler_name(self, node):
        """Get handler name for the given node.

        Args:
            node: Document node to process.

        Returns:
            Name (alias) or ``None``.

        See Also:
            :meth:`call_handler`.
        """
        raise NotImplementedError

    def do_process_node(self, node):
        """Process given node.

        By default it searches node's handler and calls it.

        Args:
            node: Document node to process.

        See Also:
            :meth:`get_handler_name`, :meth:`call_handler`.
        """
        name = self.get_handler_name(node)
        if name is not None:
            self.call_handler(name, node)

    def do_process(self):
        """Process document nodes to collect sections.

        By default it iterates over tol level nodes.
        """
        # Make a copy of children because there may be modifications.
        for node in self.document.children[:]:
            self.do_process_node(node)

    def after_process(self):
        """Hook to run actions after document processing."""
        pass

    def apply(self, *kwargs):
        if not hasattr(self.document, 'field_sections'):
            # NOTE: known sections will be handled firstly and then others.
            # So we use ordered dict to have constant order for others.
            self.document.field_sections = OrderedDict()

        self.do_process()
        self.do_remove_nodes()
        self.after_process()


class AddCollectedSectionsBase(DocumentTransform):
    """Base class to add collected sections back to the document."""

    def __init__(self, *args, **kwargs):
        super(AddCollectedSectionsBase, self).__init__(*args, **kwargs)

    def apply(self, **kwargs):
        self.add_sections(self.document)

    def do_add_section(self, node, sections, name):
        """Add section to the given node.

        Before adding the section it calls ``process_<name>(section)`` if
        the method is defined. The hook can modify the section somehow.

        Args:
            node: Parent node for the section.
            sections: Sections dict.
            name: Name of the section to add.
        """
        section = sections.get(name)
        if section is not None:
            h = getattr(self, 'process_' + name, None)
            if h is not None:
                h(section)
            node += section

    def add_sections(self, node):
        """Add sections to the given node.

        Args:
            node: Parent sections node.

        See Also:
            :meth:`do_add_section`.
        """
        sections = self.document.field_sections
        order = self.document.env['settings']['section_order']
        other_names = (x for x in sections.keys() if x not in order)

        # At first, add ordered sections then others.
        for name in chain(order, other_names):
            self.do_add_section(node, sections, name)

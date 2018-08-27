"""
This module provides docstring nodes.
"""
from docutils import nodes
from ..report import Codes
from .utils import add_report


def copy_basic_data(src, dest):
    """Helper function to copy essential data from the source node.

    It used to create ``src`` node replacement with different type.
    """
    dest.source = src.source
    dest.line = src.line
    dest.document = src.document


class invisible_marker(nodes.Element):
    """Special internal node."""
    pass


class docstring_section(nodes.Sequential, nodes.Element):
    """Represent docstring section - logically grouped nodes.

    It can be a list of detected parameters or other fields,
    or list of examples etc.
    """
    def __init__(self, name, first_node=None):
        """Construct a section.

        Args:
            name: Section name
            first_node: Original node which triggers section building.
                It used to to copy metadata (source, line number, document).
        """
        nodes.Element.__init__(self, name=name)
        if first_node is not None:
            copy_basic_data(first_node, self)


# http://www.sphinx-doc.org/en/stable/domains.html#info-field-lists
class info_field(nodes.Part, nodes.Element):
    """Base class for the info field.

    Structure::

        <info_field orig_field_tag="...">
            <body_class>...</body_class>
        </info_field>

    * ``orig_field_tag`` - original tag.
    * :class:`body_class` - Info field description (optional).
    """

    #: Node class for the body.
    body_class = None

    def __init__(self, field_node, field_tag, *children, **attributes):
        attributes['orig_field_tag'] = field_tag
        src = field_node.rawsource if field_node is not None else ''
        nodes.Element.__init__(self, rawsource=src, *children, **attributes)
        if field_node is not None:
            copy_basic_data(field_node, self)
        self.copy_body(field_node)

    def copy_body(self, field_node):
        """Copy children of the ``field_node`` to this node.

        It adds instance of the :attr:`body_class` to the :attr:`children`.

        If :attr:`body_class` is not set then do nothing.

        Args:
            field_node: :class:`nodes.field` instance.
        """

        if self.body_class is not None:
            if field_node is not None and len(field_node):
                orig_body = field_node[1]
                body = self.body_class(orig_body.rawsource, *orig_body.children)
                copy_basic_data(orig_body, body)
            else:
                body = self.body_class()
            self.append(body)

    def to_str(self):
        """String representation of the info field tag."""
        return u':{}:'.format(self['orig_field_tag'])


class info_field_with_type(info_field):
    """Extends :class:`info_field` with type specification.

    Structure::

        <info_field_with_type type="..." orig_field_tag="...">
            <body_class>...</body_class>
        </info_field_with_type>

    """
    def __init__(self, field_node, field_tag, *children, **attributes):
        info_field.__init__(self, field_node, field_tag, *children,
                            **attributes)

    def add_type(self, type_spec, type_node=None):
        """Add field type.

        Args:
            type_spec: type specification.
            type_node: Node with type specification.

        Returns:
            True: if type is added.
            False: if type specification is incorrect or already exists.
                Error message will be added to the document's reporter.
        """
        if '\n' in type_spec:
            if type_node is not None:
                type_str = type_node[0].astext()
            else:
                type_str = self.to_str()
                type_node = self

            add_report(
                type_node,
                Codes.COMPLEX,
                'Type specification is too complex [:{}:]'.format(type_str)
            )
            return False

        if 'type' in self:
            type_list = self['type']
            if type_spec in type_list:
                if type_node is not None:
                    type_str = u':{}:'.format(type_node[0].astext())
                else:
                    type_str = self.to_str()
                    type_node = self

                add_report(
                    type_node,
                    Codes.DUPLICATE,
                    'Duplicate type declaration [{}] for [{}]'.format(
                        type_str, self.to_str())
                )
                return False
            else:
                self['type'].append(type_spec)
                if ' ' in type_spec:
                    self['has_complex_type'] = True
        else:
            self['type'] = [type_spec]
            if ' ' in type_spec:
                self['has_complex_type'] = True

        return True

    def add_type_from_node(self, type_node):
        """Add field type.

        Args:
            type_node: Node with type info. It's first child must provide
                type specification.

        Returns:
            True: if ``type_node`` is valid and type is set.
            False: if type specification is incorrect or this node already has
                type. Error message will be added to the domain reporter.
        """
        type_txt = type_node[1].astext()
        return self.add_type(type_txt, type_node)


class param_field_body(nodes.field_body):
    """Body container for the :class:`param_field`."""
    pass


class param_field(info_field_with_type):
    """Represents ``:param:`` field.

    Structure::

        <param_field name="..." type="..." orig_field_tag="...">
            <param_field_body>...</param_field_body>
        </param_field>

    * ``name`` - parameter name.
    * ``type`` - parameter type (if specified).
    * ``orig_tag`` - original tag.
    * :class:`param_body` - parameter description.
    """
    body_class = param_field_body

    def __init__(self, name, field_node, field_tag, *children, **attributes):
        attributes['name'] = name
        info_field_with_type.__init__(self, field_node, field_tag, *children,
                                      **attributes)

    def to_str(self):
        """String representation of the info field tag."""
        return u':{} {}:'.format(self['orig_field_tag'], self['name'])


class return_field_body(nodes.field_body):
    """Body container for the :class:`return_field`."""
    pass


class return_field(info_field_with_type):
    """Represents ``:returns:`` field.

    Structure::

        <return_field type="..." orig_tag="...">
            <return_field_body>...</return_field_body>
        </return_field>
    """
    body_class = return_field_body

    @classmethod
    def create_from_type(cls, type_node):
        node = cls(nodes.field(), 'returns')
        copy_basic_data(type_node, node)
        node.add_type_from_node(type_node)
        return node


class raises_field_body(nodes.field_body):
    """Body container for the :class:`raises_field`."""
    pass


class raises_field(info_field_with_type):
    """Represents ``:raises:`` field.

    Structure::

        <raises_field type="..." orig_tag="...">
            <raises_field_body>...</raises_field_body>
        </raises_field>
    """
    body_class = raises_field_body


class yields_field_body(nodes.field_body):
    """Body container for the :class:`yields_field`."""
    pass


class yields_field(info_field_with_type):
    """Represents ``:Yields:`` field.

    Structure::

        <yields_field type="..." orig_tag="...">
            <yields_field_body>...</yields_field_body>
        </yields_field>
    """
    body_class = yields_field_body


class seealso(nodes.Admonition, nodes.Element):
    """Node for the ``seealso`` directive."""
    pass


class todo(nodes.Admonition, nodes.Element):
    """Node for the ``todo`` directive."""
    pass

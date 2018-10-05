from docutils.nodes import field_list, field, paragraph, Text, reference
from ....docstring.transforms.field_sections import CollectSectionsBase
from ....docstring import nodes as docstring_nodes
from ....report import Codes


# TODO: add 'var, cvar + vartype'.
# http://www.sphinx-doc.org/en/stable/domains.html#info-field-lists
class CollectInfoFields(CollectSectionsBase):
    """This transform collects info fields into sections.

    Original nodes will be removed from the document.
    Sections are saved in the :attr:`document.field_sections` dict.

    The following nodes are collected:

        * Parameters and types (``:param:``, ``:type:`` and aliases)
          are collected to the *params* section.

        * Returns (``:return:``, ``:rtype:``) are collected to the *returns*
          section.

        * Raises (``:raises:`` and aliases) are collected to the *raises*
          section.

        * ``:Yields:`` are collected to the *yields* section.
    """

    def __init__(self, *args, **kwargs):
        super(CollectInfoFields, self).__init__(*args, **kwargs)
        self.set_handler_aliases('return', ['return', 'returns'])
        self.set_handler_aliases('raises', ['raises', 'raise', 'except',
                                            'exception'])
        self.set_handler_aliases('param', ['param', 'parameter', 'arg',
                                           'argument', 'key', 'keyword',
                                           'ivar'])
        self.param_types_map = {}
        self.params_map = {}
        self.placed_info_field_marker = False

    # def clear(self):
    #     super(CollectInfoFields, self).clear()
    #     self.param_types_map.clear()
    #     self.params_map.clear()
    #     self.placed_info_field_marker = False

    def get_handler_name(self, node):
        raise NotImplementedError('Not used, see do_process_node()')

    def do_process_node(self, node):
        if isinstance(node, field_list):
            # Make a copy of children because there may be modifications.
            for el in node.children[:]:
                if not isinstance(el, field):
                    continue

                # <field><field_name>...</field_name><field_body/></field>

                # If there are multiple children then probably param name
                # contains some RST construction.
                # Currently only reference construction is supported: <name>_
                # TODO: test me.
                if len(el.children[0]) > 1:
                    field_signature_parts = []
                    for e in el.children[0]:
                        # Parameter name is <name>_ which is parsed as RST
                        # reference. We should handle it as a plain text.
                        if isinstance(e, reference):
                            field_signature_parts.append(e.astext() + '_')
                        else:
                            field_signature_parts.append(e.astext())
                    field_signature = ' '.join(field_signature_parts)
                else:
                    field_signature = el.children[0].children[0]

                parts = field_signature.split()
                fieldname = parts.pop(0)
                ok = self.call_handler(fieldname, el, fieldname=fieldname,
                                       parts=parts)

                # Put marker right before the field list.
                if ok and not self.placed_info_field_marker:
                    i = self.document.index(el.parent)
                    m = docstring_nodes.invisible_marker()
                    self.document.insert(i, m)
                    self.placed_info_field_marker = True

    def after_process(self):
        if not self.placed_info_field_marker:
            self.document += docstring_nodes.invisible_marker()

        # Go over param types and assign attributes to related params.
        params_map = self.params_map
        for section_name, types in self.param_types_map.items():
            section = params_map.get(section_name)

            if section is None:
                self.reporter.add_report(
                    Codes.UNKNOWN, 'Unknown field section [%s]' % section_name)
                continue

            for param_name, type_nodes in types.items():
                param_node = section.get(param_name)

                if not param_node:
                    type_node = type_nodes[0]
                    self.reporter.add_report(
                        Codes.UNKNOWN,
                        'Type for unknown parameter [%s]' % param_name)
                    continue

                # TODO: if returns false then remove it?
                for node in type_nodes:
                    param_node.add_type_from_node(node)

    # :param str sender: ...
    # :param sender: ...
    # Convert field to param_field.
    #
    # :keyword: and :key:
    def process_param(self, node, fieldname, parts):
        # This is just a  ':param:'. We drop it.
        if not parts:
            self.reporter.add_report(
                Codes.INCORRECT, 'Incorrect signature [:%s:]' % fieldname)
            self.add_to_remove(node)
            return

        param_name = parts.pop()

        if fieldname in ('keyword', 'key'):
            section_name = 'keyword'
        elif fieldname == 'ivar':
            section_name = 'attributes'
        else:
            section_name = 'params'

        param_section = self.params_map.setdefault(section_name, dict())

        # Duplicate param def.
        # TODO: Check what param has more info and keep only longest?
        # For now keep in the document.
        if param_name in param_section:
            self.reporter.add_report(
                Codes.DUPLICATE,
                'Duplicate field [:%s %s:]' % (fieldname, param_name))
            self.add_to_remove(node)
            return

        # Mark as param for the :type: handler.
        # It checks this attr for validation.
        node['is_param'] = True

        param = docstring_nodes.param_field(param_name, node, fieldname)
        if parts:
            param.add_type(u' '.join(parts))

        param_section[param_name] = param
        # self.params_map[section_name][param_name] = param

        section = self.get_docstring_section(section_name, node)
        section += param

        self.add_to_remove(node)

    # :type name: ...
    # :kwtype name: ...
    def process_type(self, node, fieldname, parts):
        # This means :type: or :type many words here:
        # Must be :type name:. We drop it.
        # TODO: can we recover?
        # For example we can take last part and search for existing parameter.
        # If exists then probably we can do:
        # :type bla bla name:  ->  :type name: bla bla
        if not parts or len(parts) > 1:
            self.reporter.add_report(
                Codes.INCORRECT, 'Incorrect signature [:%s:]' % fieldname)
            self.add_to_remove(node)
            return

        param_name = parts.pop()

        # # TODO: what to do with duplicate type? Drop it?
        # # Maybe do the same as for param - keep the one with longest content.
        # # (or shortest).
        # # For now keep in the document.
        # if param_name in self.param_types_map:
        #     node.document.reporter.error(
        #         'Duplicate type declaration for the parameter [%s]'
        #         % (param_name), base_node=node, autodoc=True
        #     )
        #     self.add_to_remove(node)
        #     return

        # Collect and postpone processing - this is to collect all parameters.
        # If type is specified before param this can help to recover
        # and link to correct param.
        # NOTE: Name is the same as for self.params_map, see process_param().
        if fieldname == 'kwtype':
            section_name = 'keyword'
        elif fieldname == 'vartype':
            section_name = 'attributes'
        else:
            section_name = 'params'

        types = self.param_types_map.setdefault(section_name, dict())
        types.setdefault(param_name, []).append(node)
        # self.param_types_map.setdefault(param_name, []).append(node)
        self.add_to_remove(node)

    process_kwtype = process_type
    process_vartype = process_type

    # :return: ...
    def process_return(self, node, fieldname, parts):
        # If :return: has extra text inside (:return bla bla:)
        # then we keep in the document.
        if parts:
            self.reporter.add_report(
                Codes.INCORRECT, 'Incorrect signature [:%s:]' % fieldname)
            self.add_to_remove(node)
            return

        # Check if there is a description.
        if not len(node[1]):
            self.reporter.add_report(
                Codes.EMPTY, 'Empty content [:%s:]' % fieldname)
            self.add_to_remove(node)
            return

        # Mark as return field for the :rtype: handler.
        # It checks this attr for validation.
        node['is_return'] = True

        ret = docstring_nodes.return_field(node, fieldname)

        section = self.get_docstring_section('returns', node)
        section += ret

        self.add_to_remove(node)

    # :rtype: ...
    # TODO: where to store rtype?
    # TODO: what if rtype is placed before returns?
    def process_rtype(self, node, fieldname, parts):
        # If :rtype: has extra text inside (:rtype bla bla:)
        # then we keep in the document.
        if parts:
            self.reporter.add_report(
                Codes.INCORRECT, 'Incorrect signature [:%s:]' % fieldname)
            self.add_to_remove(node)
            return

        # Check body.
        # :rtype: assumed to have simple paragraph with type or list of types.
        # No line breaks or complex formatting.
        #
        # NOTE: One more check performs in  add_type_from_node() method later.
        # Here we just check if there more than one children (paragraphs).
        #
        # TODO: what to do?
        # For now keep in the document.
        if len(node[1]) != 1:
            self.reporter.add_report(
                Codes.COMPLEX,
                'Type specification is too complex [:%s:]' % fieldname)
            self.add_to_remove(node)
            return

        # Get previous node.
        i = node.parent.index(node) - 1
        prev_node = node.parent[i] if i != -1 else None

        create_own_field = False

        # :rtype: is placed not after :returns:
        # We create separate returns field for the type.
        if prev_node is None or not prev_node.get('is_return'):
            create_own_field = True

        # :rtype: is placed after :returns:
        else:
            section = self.get_docstring_section('returns')
            # Get last detected return and try to attach type to it.
            if section:
                ret = section[-1]
                # If type if not set then attach.
                if 'type' not in ret:
                    ret.add_type_from_node(node)
                # Otherwise create separate field.
                else:
                    # NOTE: this case can't happen:
                    # :rtype: is placed after :returns: and :returns: has type.
                    # Because only :rtype: sets type. But we keep to not loose
                    # type info in cases :returns: will have type somehow in
                    # future (is that possible?)
                    create_own_field = True

        if create_own_field:
            section = self.get_docstring_section('returns', node)
            ret = docstring_nodes.return_field.create_from_type(node)
            section += ret

        self.add_to_remove(node)

    # :raises ValueError: ...
    def process_raises(self, node, fieldname, parts):
        rnode = docstring_nodes.raises_field(node, fieldname)

        num_parts = len(parts)
        # If it's :raises: without a type.
        if not num_parts:
            self.reporter.add_report(
                Codes.MISSING, 'Type is missing [:%s:]' % fieldname)
            if not len(rnode.children[0]):
                self.reporter.add_report(
                    Codes.MISSING, 'Description is missing [:%s:]' % fieldname)
                self.add_to_remove(node)
                return

        # If :raises Type: has extra text inside (:raises Type bla:)
        # We move it to the description.
        elif num_parts > 1:
            self.reporter.add_report(
                Codes.INCORRECT, 'Incorrect signature [:%s:]' % fieldname)
            text = ' '.join(parts)
            # Try to insert incorrect text into description to not lose it.
            try:
                add = text if text.endswith('.') else text + '.'
                rnode[0][0].insert(0, Text(add + ' '))
            except Exception as e:
                rnode[0].insert(0, paragraph(text=text))

        else:
            rnode['type'] = [parts[0]]

        section = self.get_docstring_section('raises', node)
        section += rnode

        self.add_to_remove(node)

    # :Yields: ...
    def process_yields(self, node, fieldname, parts):
        # If :Yields: has extra text inside (:Yields bla bla:)
        if parts:
            self.reporter.add_report(
                Codes.INCORRECT, 'Incorrect signature [:%s:]' % fieldname)
        elif not len(node[1]):
            self.reporter.add_report(
                Codes.MISSING, 'Content is missing [:%s:]' % fieldname)
        else:
            yields_node = docstring_nodes.yields_field(node, 'Yields')
            section = self.get_docstring_section('yields', node)
            section += yields_node
        self.add_to_remove(node)

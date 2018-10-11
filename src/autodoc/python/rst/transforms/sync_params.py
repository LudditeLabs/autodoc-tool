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

from ....docstring.transforms.base import DocumentTransform
from ....docstring import nodes as docstring_nodes
from ....report import Codes
from ....contentdb import DefinitionType


class SyncParametersWithSpec(DocumentTransform):
    """This transform syncs docstring parameters with ones specified in the
    ``document.docstring_ref``.

    The following actions are performed:

    * Add missing parameters.
    * Remove parameters not listed in the ``document.docstring_ref.args``.
    * Sort parameters according to ``document.docstring_ref.args`` order.
    * Update parameters types if required.

    Docstring parameters are collected by the :class:`CollectInfoFields`.
    """

    def apply(self, **kwargs):
        # Do nothing if parameters specification is not set or
        # it's not a function/method.
        definition = self.env['definition']

        need_sync = False

        if (definition.type is DefinitionType.CLASS
                and definition.args is not None):
            need_sync = True

        elif (definition.type is DefinitionType.MEMBER
              and definition.is_function):
            need_sync = True

        if not need_sync:
            return

        # Do nothing if sections are not collected.
        # See collect_fields.CollectInfoFields.
        sections = getattr(self.document, 'field_sections', None)
        if sections is None:
            return

        # Is this docstring missing?
        # If yes then we don't report about missing stuff.
        is_missing = self.env.get('missing', False)

        # Add params section if not exists but don't save in sections for
        # a moment.
        params = sections.get('params')
        if params is None:
            params = docstring_nodes.docstring_section('params')
            params.source = self.document.source
            params.document = self.document
            sections['params'] = params

        # params is a nodes.docstring_section instance which has children
        # Map of name -> [order index, node]
        param_map = {x['name']: (i, x) for i, x in enumerate(params.children)}

        real_param_list = []
        na = (None, None)

        # NOTE: we expect arg_type to be a list of params!
        args = definition.args or ()

        # For methods except static ones we ignore first argument (self or cls)
        # Static method has no such arg.
        if (args and definition.type is DefinitionType.MEMBER
                and definition.is_method
                and not definition.is_static):
            args = args[1:]

        for arg in args:
            pos, param = param_map.pop(arg.name, na)

            # If param is not exists then create one.
            if param is None:
                param = docstring_nodes.param_field(arg.name, None, 'param')
                param.parent = params
                if arg.type_list:
                    param['type'] = arg.type_list

                if not is_missing:
                    self.reporter.add_report(
                        Codes.MISSING,
                        'Missing parameter [{}]'.format(arg.name))

            else:
                # Check types.
                if arg.type_list:
                    type_list = param.get('type')
                    if type_list != arg.type_list:
                        param['type'] = arg.type_list
                        if not is_missing:
                            self.reporter.add_report(
                                Codes.MISMATCH,
                                'Parameter type is different [{}]'.format(
                                    arg.name)
                            )
                # Check order.
                if pos != len(real_param_list):
                    self.reporter.add_report(
                        Codes.INCORRECT,
                        'Parameter order is incorrect [{}]'.format(arg.name))

            real_param_list.append(param)

        params.children = real_param_list

        for name, (_, node) in param_map.items():
            self.reporter.add_report(Codes.UNKNOWN,
                                     'Unknown parameter [{}]'.format(name))

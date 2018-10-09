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

from ...report import Codes
from .base import DocumentTransform


class MarkMissingDocstring(DocumentTransform):
    """This transform reports about missing or empty docstring.

    It also sets ``missing=True`` in ``document.env`` if docstring is
    missing.

    * Docstring is considered *missing* if it has no lines.
    * Docstring is considered *empty* if it has only blank lines lines.
    """

    def apply(self, **kwargs):
        definition = self.env['definition']
        if definition.doc_block.docstring is None:
            self.env['missing'] = True
            self.reporter.add_report(Codes.NODOC, 'Missing docstring.', 0, 0)
        elif not len(self.document):
            self.reporter.add_report(Codes.NODOC, 'Empty docstring.', 0, 0)

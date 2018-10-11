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

from docutils.writers import Writer


class TextWriter(Writer):
    def __init__(self, translator_cls):
        super(TextWriter, self).__init__()
        self.translator_cls = translator_cls

    def get_transforms(self):
        return []

    def translate(self):
        visitor = self.translator_cls(self.document)
        self.document.walkabout(visitor)
        docstring = visitor.output

        # If result docstring has no lines then check if we need to add some.
        if not docstring:
            settings = self.document.env['settings']
            num_lines = settings['empty_docstring_lines']
            if num_lines:
                docstring = [u''] * num_lines

        if docstring:
            self.output = '\n'.join(docstring)

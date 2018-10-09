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

from docutils.readers import Reader as _Reader
from docutils.io import StringInput


class Reader(_Reader):
    """This reader subscribes autodoc domain reporter on parser's messages."""
    def __init__(self, parser=None, parser_name=None):
        super(Reader, self).__init__(parser=parser, parser_name=parser_name)
        self.env = None

    def new_document(self):
        document = super(Reader, self).new_document()
        if self.env is not None and self.env['reporter'] is not None:
            document.reporter.attach_observer(
                self.env['reporter'].document_message)
        document.env = self.env
        return document

    def clear(self):
        self.env = None


class TextReader(Reader):
    """This reader accepts text as source."""
    def read(self, source, parser, settings, **params):
        source = StringInput(source=source, **params)
        return super(TextReader, self).read(source, parser, settings)

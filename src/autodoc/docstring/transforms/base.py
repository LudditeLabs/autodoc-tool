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

from docutils.transforms import Transform


class DocumentTransform(Transform):
    """Base document transform."""

    default_priority = 999

    def __init__(self, document, startnode=None):
        super(DocumentTransform, self).__init__(document, startnode)
        self.env = document.env
        self.reporter = self.env['reporter']

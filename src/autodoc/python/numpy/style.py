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

from ..style_napoleon import NapoleonStyleTransform, NapoleonStyle
from ..napoleon import NumpyDocstring
from .translator import DocumentToNumpyTranslator


# TODO: implement me.
class FromNumpyStyleTransform(NapoleonStyleTransform):
    """Convert NumPy style docstrings to reStructuredText."""

    name = 'numpy'
    converter = NumpyDocstring

    def __init__(self, reporter):
        super(FromNumpyStyleTransform, self).__init__(reporter)
        self.cfg.napoleon_numpy_docstring = True

    # TODO: implement me
    def sanitize(self, lines, has_sections):
        return lines


class NumpyStyle(NapoleonStyle):
    """Pipeline to translate docstring document to Google style format."""

    name = 'numpy'

    settings_section = name
    settings_spec_help = 'NumPy docstring style.'

    document_translator_cls = DocumentToNumpyTranslator
    docstring_transform_cls = FromNumpyStyleTransform

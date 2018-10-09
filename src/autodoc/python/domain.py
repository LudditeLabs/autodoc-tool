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

from ..domain import LanguageDomain
from ..task import SkipProcessing, DefinitionHandlerTask, FileSyncTask
from .rst import RstStyle
from .google import GoogleStyle
from .numpy import NumpyStyle
from ..docstring.transforms.missing_docstring import MarkMissingDocstring
from .rst.transforms.collect_fields import CollectInfoFields
from .rst.transforms.sync_params import SyncParametersWithSpec
from ..settings import C
from ..contentdb import DefinitionType


class PyDefinitionHandlerTask(DefinitionHandlerTask):
    transforms = (MarkMissingDocstring, CollectInfoFields,
                  SyncParametersWithSpec)

    def setup(self):
        # NOTE: doxygen sets 'bodystart' to the line with colon, not to actual
        # body start as python's ast parser does::
        #
        #   def foo():  # <- bodystart
        #       pass
        #
        #   def foo(bla,
        #           bla2):  # <- bodystart
        #       pass
        #
        #   def foo()
        #       :  # <- bodystart
        #       pass
        #
        # Also 'bodyend' is set to line before next definition or EOL::
        #
        #   def foo():
        #       pass
        #               # <- bodyend
        #   def bar():
        #       pass    # <- bodyend
        #   def foo_1(): pass
        #               # <- bodyend
        #   def bar_1():
        #       pass
        #
        super(PyDefinitionHandlerTask, self).setup()

        # This is one line function, skip processing.
        if (self.definition.type is DefinitionType.MEMBER
                and self.definition.bodyend - self.definition.bodystart <= 1):
            raise SkipProcessing

        docstring_level = self.settings['class_docstring_level']

        if docstring_level == 'self':
            self.move_docstring_to_class()
        elif docstring_level == 'init':
            self.move_docstring_to_init()

        # For all other values process class and __init__ separately.

        self.normalize_doc_block()

    def append_dostring(self, src, dest, copy_args=False):
        """Append docstring from one definition to another.

        Args:
            src: Source definition.
            dest: Destination definition.
            copy_args: Copy args from the source.
        """
        if src:
            if src.doc_block.docstring:
                dest.doc_block.docstring = (
                        (dest.doc_block.docstring or '')
                        + '\n\n'
                        + src.doc_block.docstring
                )
            if copy_args and src.args:
                # Skip first 'self' arg
                dest.args = src.args[1:]

    def move_docstring_to_class(self):
        """Combine class and ``__init__`` method docstrings and put result
        to class docstring.

        ``__init__`` method docstring is removed when the task processes
        corresponding definition.
        """

        # If current definition is class then get __init__ docstring and append
        # to the definition's one.
        if self.definition.type is DefinitionType.CLASS:
            ctor = self.db.get_constructor(self.definition.id)
            self.append_dostring(src=ctor, dest=self.definition, copy_args=True)

        # If current definition is __init__ method then set flag to skip
        # processing and remove its docstring.
        # The flag is used in DefinitionHandlerTask.do_run().
        elif (self.definition.type is DefinitionType.MEMBER
              and self.definition.name == '__init__'):
            self.remove_docstring = True

    def move_docstring_to_init(self):
        if self.definition.type is DefinitionType.CLASS:
            # Append class docstring to __init__ docstring then
            # save __init__ doc block changes.
            ctor = self.db.get_constructor(self.definition.id)
            if ctor:
                self.append_dostring(src=self.definition, dest=ctor)
                self.normalize_doc_block(ctor)
                self.db.save_doc_block(ctor)

            # Remove class docstring.
            self.remove_docstring = True

        elif (self.definition.type is DefinitionType.MEMBER
              and self.definition.name == '__init__'):
            pass

    def normalize_doc_block(self, definition=None):
        """Setup docblock indent."""
        definition = definition or self.definition
        doc = definition.doc_block
        if doc.id is None:
            doc.refid = definition.refid
            doc.type = definition.type
            doc.id_file = definition.id_file
            if definition is DefinitionType.MEMBER:
                doc.start_line = definition.bodystart
            else:
                doc.start_line = definition.start_line
            # TODO: detect indent.
            doc.start_col = definition.start_col + 4
            doc.end_line = None
            doc.end_col = None


class PyFileSyncTask(FileSyncTask):
    def prepare(self, docblock):
        # Surround docstring with quotes.
        if docblock.docstring is not None:
            quote = self.settings['docstring_quote']
            docblock.docstring = quote + docblock.docstring + quote


class PythonDomain(LanguageDomain):
    name = 'python'
    extensions = ['.py', '.pyw']

    settings_section = 'py'
    settings_spec_help = 'Python language.'
    settings_spec = LanguageDomain.settings_spec + (
        ('Output docstring style.', 'style', 'google'),
        ('Quote to use for docstrings.', 'docstring_quote', '"""'),
        (
            'List of sections in order of following in the docstring.',
            'section_order',
            [
                'todo',
                'example',
                'examples',
                'attributes',
                'params',
                'keyword',
                'returns',
                'raises',
                'yields',
                'methods',
                'warnings',
                'note',
                'notes',
                'seealso',
                'references',
            ]
        ),
        ("""Where to put class docstring.
        
         The __init__ method may be documented in either the class level
         docstring, or as a docstring on the __init__ method itself.

         self - keep docstring in class, __init__ docstring is appended.
         init - keep docstring in __init__, class docstring is prepended.
         separate - process class and __init__ docstrings separately.
         """,
         'class_docstring_level', 'separate', C('self', 'init', 'separate')),
    )

    settings_spec_nested = LanguageDomain.settings_spec_nested + (
        RstStyle, GoogleStyle, NumpyStyle
    )

    docstring_styles = (RstStyle, GoogleStyle, NumpyStyle)

    definition_handler_task = PyDefinitionHandlerTask
    file_sync_task = PyFileSyncTask

    def __init__(self):
        super(PythonDomain, self).__init__()

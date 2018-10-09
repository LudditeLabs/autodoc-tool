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

from .report import DomainReporter
from .settings import SettingsSpec
from .task import SkipProcessing


class LanguageDomain(SettingsSpec):
    #: Domain name (language).
    #:
    #: It used as a display name in the reports and also it defines
    #: source language name.
    name = None

    #: Supported files extensions.
    extensions = None

    settings_spec = (
        ('Input docstring style.', 'instyle', 'all'),

        ('Docstring width.', 'line_width', 80, (None, int)),
        ('Default indentation for nested constructions.', 'indent', 4),
        ('Entire docstring indentation.', 'indent_global', 0),

        (
            """
            Make sure first line is blank.
            None means have blank line only for multi line docstring.
            False - no blank lines
            True - add single blank line
            <num> - number of blank lines.
            """,
            'first_blank_line', False, (None, bool, int)
        ),

        (
            """
            Make sure last line is blank.
            None means have blank line only for multi line docstring.
            False - no blank lines
            True - add single blank line
            <num> - number of blank lines.
            """,
            'last_blank_line', None, (None, bool, int)
        ),

        # For example:
        #     :strong:`strong` -> **strong**
        #     :title-reference:`Title ref` -> :t:`Title ref`
        ('Use shorter version of the inline markup.', 'shorten_inline', True),

        (
            """
            Number of lines to add to empty/missing docstring.
            Zero means remove empty docstring.
            """,
            'empty_docstring_lines', 0
        ),
    )

    docstring_styles = None
    definition_handler_task = None
    file_sync_task = None

    def __init__(self):
        self.reporter = DomainReporter(self)
        self.context = None

        lst = self.docstring_styles or []
        self._styles = [x(self) for x in lst]
        self._styles_map = {x.name: x for x in self._styles}
        self._styles_transforms = [x.transform_docstring for x in self._styles]

    @property
    def logger(self):
        return self.context.logger

    @property
    def settings(self):
        return self.context.settings

    @property
    def styles(self):
        """List of styles instances.

        The list is built from list of style classes in
        :attr:`docstring_styles`.
        """
        return self._styles

    def get_style(self, name):
        """Get style by name.

        Args:
            name: Style name.

        Returns:
            :class:`DocstringStyle` instance or ``None``.
        """
        return self._styles_map.get(name)

    def create_env(self, **kwargs):
        """Create task environment dict.

        Args:
            **kwargs: Extra env vars.

        Returns:
            Task environment dict.
        """
        env = {
            'db': kwargs.pop('content_db'),
            'reporter': self.reporter,
            'settings': self.settings,
        }
        env.update(kwargs)
        return env

    def create_task(self, name, env):
        """Create task.

        This method creates instance of a class specified in the attribute
        ``<name>``.

        Args:
            name: Task name.
            env: Task environment.

        Returns:
            Task instance.
        """
        task_cls = getattr(self, name)
        return task_cls(self, env)

    def run_task(self, name, **kwargs):
        """Run task.

        Args:
            name: Task name.
            **kwargs: Task environment.
        """
        env = self.create_env(**kwargs)
        self.reporter.env = env
        task = self.create_task(name, env)
        try:
            task.run()
        except SkipProcessing:
            pass
        self.reporter.reset()

    def process_definition(self, content_db, definition):
        """Process given definition (class, function, method etc).

        Args:
            content_db: :class:`ContentDb` instance.
            definition: :class:`Definition` instance.
        """
        with self.settings.from_key('style'):
            self.run_task('definition_handler_task', content_db=content_db,
                          report_filename=definition.filename,
                          definition=definition)

    def sync_sources(self, content_db, out_filename=None):
        """Sync sources with content in the given DB.

        Args:
            content_db: :class:`ContentDb` instance.
            out_filename: Output filename (set if there is only one file to
                sync).
        """
        with self.settings.from_key('style'):
            for id, filename in content_db.get_domain_files(self):
                self.run_task('file_sync_task', content_db=content_db,
                              report_filename=filename,
                              file_id=id, filename=filename,
                              out_filename=out_filename)

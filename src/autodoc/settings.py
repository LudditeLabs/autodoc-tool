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

from textwrap import dedent
import os.path as op
import json
import yaml
import copy
from contextlib import contextmanager
try:
    from yaml import CSafeLoader as SafeLoader
except ImportError:  # pragma: nocover
    from yaml import SafeLoader
from .utils import merge_recursive, InheritDict


class SettingsSpec:
    """Class with settings specification."""

    #: Settings section name.
    settings_section = None

    #: List of settings specifications.
    #:
    #: Each item is a tuple::
    #:
    #:     (help, setting name, default value, type or tuple of types)
    #:
    #: `type` is optional.
    settings_spec = ()

    #: Help string for the settings section.
    settings_spec_help = None

    #: List of nested settings specs.
    settings_spec_nested = ()


def read_config_file(source, fmt=None):
    """Read configuration from the source.

    Configuration may be in JSON or YAML format.

    Args:
        source: Filename or file-like object.
        fmt: Source format if file-like object is provided.

    Raises:
        ValueError: If root object is not a dictionary.
        IOError: If file is not found.

    Returns:
        Dict with values.
    """
    if isinstance(source, str):
        f = open(source)
        if fmt is None:
            _, ext = op.splitext(source)
            if ext in ('.yml', '.yaml'):
                fmt = 'yaml'
            elif ext == '.json':
                fmt = 'json'
    else:
        if fmt is None:
            raise ValueError('Configuration format is not set.')
        f = source

    if fmt == 'json':
        data = json.load(f)
    elif fmt == 'yaml':
        data = yaml.load(f, Loader=SafeLoader)
    else:
        raise IOError('Unknown configuration format.')

    if not isinstance(data, dict):
        raise ValueError('Not a dictionary.')
    return data


class Spec:
    """Setting specification.

    This class contains help string and allowed value type. It can validate
    values and convert strings to the type.

    Args:
        name: Setting name.
        help: Setting help string.
        type: Setting type. If ``None`` then can be of any type.
    """
    def __init__(self, name, help=None, type=None):
        self.name = name
        self.help = help
        self.type = type

    def do_validate(self, value):
        if self.type is not None:
            return type(value) is self.type
        return True

    def validate(self, value):
        """Validate given ``value``.

        Args:
            value: Setting value.

        Raises:
            ValueError: if given ``value`` is incorrect.
        """
        if not self.do_validate(value):
            raise ValueError('Incorrect value for [{}]: {}'.format(
                self.name, value))

    def do_convert(self, value, type_):
        """Convert given value to setting's type.

        Args:
            value: Value to convert.

        Returns:
            Value in spec's type.
        """
        if type_ is None:
            return value

        elif type_ is bool:
            value = value.lower()
            if value in ('yes', 'true'):
                return True
            elif value in ('no', 'false'):
                return False
            else:
                raise ValueError('Incorrect value for [{}]: {}'.format(
                    self.name, value))

        try:
            return type_(value)
        except ValueError as e:
            raise ValueError('Incorrect value for [{}]: {}'.format(
                self.name, e))

    def convert(self, value):
        """Convert given value to setting's type.

        Args:
            value: Value to convert.

        Returns:
            Value in spec's type.
        """
        return self.do_convert(value, self.type)

    def help_to_lines(self):
        """Convert help to list of strings."""
        if self.help:
            help = dedent(self.help).strip()
            return help.splitlines()
        return []

    def type_to_string(self, type_):
        """Get string representation of the given type.

        Args:
            type_: Type.

        Returns:
            String representation of the ``type_``.
        """
        if type_ is None:
            return 'null'
        elif type_ is bool:
            return 'yes/no'
        elif type_ in (int, float):
            return '<number>'
        elif type_ is str:
            return '<text>'
        return '<N/A>'

    def add_type_info(self, lines):
        """Add type info to the ``lines``.

        Args:
            lines: List of text lines.
        """
        lines.append('Value: %s' % self.type_to_string(self.type))

    def to_lines(self, is_section=False):
        """Get text representation of the setting specification.

        Returns:
            List of text lines.
        """
        lines = self.help_to_lines()
        if not is_section:
            self.add_type_info(lines)
        return lines


class MultiTypeSpec(Spec):
    """This class represents multi-type setting."""
    def do_validate(self, value):
        type_ = None if value is None else type(value)
        return type_ in self.type

    def convert(self, value):
        for t in self.type:
            try:
                return self.do_convert(value, t)
            except ValueError:
                pass

        raise ValueError('Incorrect value for [{}]: {}'.format(
            self.name, value))

    def add_type_info(self, lines):
        line = ', '.join(self.type_to_string(x) for x in self.type)
        lines.append('Value: %s' % line)


class ChoiceSpec(Spec):
    """This class represents choice setting."""
    def do_validate(self, value):
        return value in self.type

    def convert(self, value):
        if value not in self.type:
            raise ValueError('Incorrect value for [{}]: {}'.format(
                self.name, value))
        return value

    def add_type_info(self, lines):
        lines.append('Value: %s' % str(self.type))


class C:
    """Choice type."""
    def __init__(self, *values):
        self.values = values


class SettingsBuilder:
    """This class builds initial settings specification and values.

    The specification is used on external settings loading to validate values.
    """

    def __init__(self, logger):
        self.logger = logger
        self.specs = {}
        self.settings = {}
        self._settings_stack = []

    def push(self, settings):
        self._settings_stack.append(self.settings)
        self.settings = settings

    def pop(self):
        self.settings = self._settings_stack.pop()

    def collect(self, spec):
        """Collect settings from the given ``spec``.

        Args:
            spec: :class:`SettingsSpec` instance.
        """
        if spec.settings_section:
            settings = self.settings.setdefault(spec.settings_section, {})
            self.push(settings)
            self.specs[spec.settings_section] = Spec(spec.settings_section,
                                                     spec.settings_spec_help)

        self.add_specs(spec.settings_spec, self.settings)

        if spec.settings_spec_nested:
            for s in spec.settings_spec_nested:
                self.collect(s)

        if spec.settings_section:
            self.pop()

    def add_specs(self, spec_list, settings):
        """Add settings specifications.

        Settings specification is a tuple::

            (<help string>, <setting name>, <default value>[, type])

        If ``type`` is not specified then it will be inferred from default
        value.

        Args:
            spec_list: List of specs.
        """
        for spec in spec_list:
            spec = spec + (None,) * (4 - len(spec))
            doc, name, default, type_ = spec

            if type_ is None:
                type_ = type(default)

            if type_ is tuple:
                type_ = dict
                values = settings.setdefault(name, {})
                self.add_specs(default, values)
            else:
                settings[name] = default

            if isinstance(type_, (list, tuple)):
                s = MultiTypeSpec(name, doc, type_)
            elif isinstance(type_, C):
                s = ChoiceSpec(name, doc, type_.values)
            else:
                s = Spec(name, doc, type_)

            spec_existing = self.specs.get(name)
            if spec_existing is not None and spec_existing.type != s.type:
                self.logger.warn('WARNING: Setting [%s] already present and '
                                 'has different type.', name)

            self.specs[name] = s

    def load_config(self, filename, fmt=None):
        # 'run' is special settings block. Used in cli.
        cfg = read_config_file(filename, fmt)
        run = cfg.pop('run')
        merge_recursive(self.settings, cfg, self.validate)
        if run is not None:
            self.settings['run'] = run

    def add_from_dict(self, src):
        if src:
            merge_recursive(self.settings, src, self.validate)

    def validate(self, k, v):
        spec = self.specs.get(k)
        if spec is None:
            raise ValueError('Unknown option: %s' % k)
        spec.validate(v)

    def add_from_keyvalues(self, values):
        """Add values from list of strings in the format ``name=value``.

        String may be quoted::

            "name=value"
            'name=value'

        Args:
            values: List of key-value strings.

        Raises:
            BadParameter: If setting with the given name is not registered,
                value or string format is incorrect.

        See Also:
            :meth:`set`.
        """
        esc = ('"', "'")
        for kw in values:
            kw = kw.strip()
            if kw[0] in esc:
                kw = kw[1:]
            if kw[-1] in esc:
                kw = kw[:-1]

            try:
                name, val = kw.split('=')
            except ValueError:
                raise ValueError('Invalid format, name=value expected: %s' % kw)

            settings = self.settings
            if '.' in name:
                parts = name.split('.')
                optname = parts.pop().strip()
                for part in parts:
                    settings = settings.setdefault(part, {})
            else:
                optname = name

            spec = self.specs.get(optname)
            if spec is None:
                raise ValueError('Unknown option: %s' % name)

            settings[optname] = spec.convert(val)

    def dump(self, stream, indent=2):
        """Dump settings in YAML format.

        Args:
            stream: Output file-like object (with ``write()`` method).
            indent: Indentation for nested constructions.
        """
        d = DumpSettings(self.settings, self.specs, indent)
        d.dump(stream)

    def get_settings(self):
        return SettingsWrapper(InheritDict(copy.deepcopy(self.settings)))


class DumpSettings(object):
    """This class implements settings dumping."""
    def __init__(self, settings, specs, indent=2):
        self.settings = settings
        self.specs = specs
        self.indent = indent

    def to_string(self, val):
        if isinstance(val, str):
            if "'" in val:
                return '"%s"' % val
            elif '"' in val:
                return "'%s'" % val
            return val

        elif isinstance(val, bool):
            return 'yes' if val else 'no'

        elif val is None:
            return 'null'

        return str(val)

    def do_dump(self, settings, stream, indent):
        keys = sorted(settings.keys())
        postpone = []
        offset = ' ' * indent

        for name in keys:
            obj = settings[name]

            if isinstance(obj, dict):
                postpone.append((name, obj))
                continue

            spec = self.specs[name]
            for line in spec.to_lines():
                stream.write('%s# %s\n' % (offset, line))

            if isinstance(obj, list):
                stream.write('{}{}:\n'.format(offset, name))
                for val in obj:
                    stream.write('{}-{}\n'.format(offset, self.to_string(val)))
                stream.write('\n')
            else:
                stream.write('{}{}: {}\n\n'.format(offset, name,
                                                   self.to_string(obj)))

        for name, obj in postpone:
            spec = self.specs[name]
            if spec.help:
                for line in spec.to_lines(is_section=True):
                    stream.write('%s# %s\n' % (offset, line))
            stream.write('{}{}:\n'.format(offset, spec.name))
            self.do_dump(obj, stream, indent + self.indent)

    def dump(self, stream):
        self.do_dump(self.settings, stream, 0)


class SettingsWrapper:
    def __init__(self, settings):
        self.settings = [settings]

    def __str__(self):
        return self.settings[-1].__str__()

    def __getitem__(self, key):
        return self.settings[-1].__getitem__(key)

    def get(self, key, default=None):
        return self.settings[-1].get(key, default=default)

    def get_by_path(self, path):
        return self.settings[-1].get_py_path(path)

    def push(self, key):
        self.settings.append(self.settings[-1][key])

    def pop(self):
        self.settings.pop()

    @contextmanager
    def from_key(self, key):
        settings = self.settings[-1][key]
        try:
            self.push(settings)
            yield self
        finally:
            self.pop()

    @contextmanager
    def with_settings(self, key=None):
        try:
            self.push(key)
            yield self
        finally:
            self.pop()

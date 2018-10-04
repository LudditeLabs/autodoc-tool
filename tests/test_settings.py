import pytest
from io import StringIO
from unittest.mock import Mock
from autodoc.settings import (
    read_config_file,
    Spec,
    MultiTypeSpec,
    ChoiceSpec,
    C,
    SettingsBuilder,
    DumpSettings
)
from autodoc.utils import trim_docstring


# Test: configuration loading.
class TestLoadConfig:
    # Test: Format is not set.
    def test_read_no_fmt(self):
        with pytest.raises(ValueError) as e:
            read_config_file(StringIO())
        assert str(e.value) == 'Configuration format is not set.'

    # Test: Read JSON from a buffer.
    def test_read_json(self):
        source = StringIO(trim_docstring("""
        {
          "one": 1,
          "two": "xxx"
        }
        """, as_string=True))

        # Format is not set.
        with pytest.raises(ValueError) as e:
            read_config_file(source)
        assert str(e.value) == 'Configuration format is not set.'

        data = read_config_file(source, fmt='json')
        assert data == dict(one=1, two='xxx')

    # Test: Read JSON from a file.
    def test_read_json_file(self, tmpdir):
        source = tmpdir.join('config.json')
        source.write(trim_docstring("""
            {
              "one": 1,
              "two": "xxx"
            }
            """, as_string=True))

        data = read_config_file(str(source))
        assert data == dict(one=1, two='xxx')

    # Test: Read YAML from a buffer.
    def test_read_yaml(self):
        source = StringIO(trim_docstring("""
        one: 1
        two: xxx
        """, as_string=True))

        # Format is not set.
        with pytest.raises(ValueError) as e:
            read_config_file(source)
        assert str(e.value) == 'Configuration format is not set.'

        data = read_config_file(source, fmt='yaml')
        assert data == dict(one=1, two='xxx')

    # Test: Read JSON from a file.
    def test_read_yaml_file(self, tmpdir):
        content = trim_docstring("""
            one: 1
            two: xxx
            """, as_string=True)

        source = tmpdir.join('config.yml')
        source.write(content)
        data = read_config_file(str(source))
        assert data == dict(one=1, two='xxx')

        source = tmpdir.join('config.yaml')
        source.write(content)
        data = read_config_file(str(source))
        assert data == dict(one=1, two='xxx')

    # Test: read invalid format.
    def test_read_invalid(self, tmpdir):
        source = tmpdir.join('config.json')
        source.write(trim_docstring("""
            one: 1
            two: xxx
            """, as_string=True))
        with pytest.raises(ValueError):
            read_config_file(str(source))

        source = tmpdir.join('config.yaml')
        source.write(trim_docstring("""
            {
              "one": 1,
              "two": "xxx"
            }
            """, as_string=True))

        # YAML is a JSON superset so can read it.
        data = read_config_file(str(source))
        assert data == dict(one=1, two='xxx')

        source = tmpdir.join('config.yaml')
        source.write(trim_docstring("""
            <bla></bla>
            """, as_string=True))

        # NOTE: yaml parser returns string as is.
        with pytest.raises(ValueError):
            read_config_file(str(source))

    # Test: read unsupported format.
    def test_read_invalid_format(self, tmpdir):
        source = tmpdir.join('config.cpp')
        source.write('...')
        with pytest.raises(IOError) as e:
            read_config_file(str(source))
        assert str(e.value) == 'Unknown configuration format.'

        with pytest.raises(IOError) as e:
            read_config_file(StringIO(), fmt='yxx')
        assert str(e.value) == 'Unknown configuration format.'


# Test: Spec class.
class TestSpec:
    # Test: construct.
    def test_construct(self):
        spec = Spec('name')
        assert spec.name == 'name'
        assert spec.help is None
        assert spec.type is None

    # Test: construct with params.
    def test_construct_params(self):
        spec = Spec('name', 'help', dict)
        assert spec.name == 'name'
        assert spec.help == 'help'
        assert spec.type is dict

    # Test: do_validate().
    @pytest.mark.parametrize('value,type,valid', [
        (123, int, True),
        (123, dict, False),
        ({}, dict, True),
        ('123', str, True),
        (False, bool, True),
        (123, None, True),      # If type if not set then always return true
        ({}, None, True),
        ('321', None, True),
    ])
    def test_do_validate(self, value, type, valid):
        spec = Spec('name', type=type)
        assert spec.do_validate(value) == valid

    # Test: validate() raises an error for incorrect value.
    def test_validate(self):
        spec = Spec('name', type=int)

        with pytest.raises(ValueError) as e:
            spec.validate('321')
        assert str(e.value) == 'Incorrect value for [name]: 321'

        # No errors here.
        spec.validate(123)

    # Test: convert string to value with spec's type.
    @pytest.mark.parametrize('value,type,result', [
        (123, int, 123),
        ('123', int, 123),
        ('123', str, '123'),
        ('yes', bool, True),
        ('TruE', bool, True),
        ('no', bool, False),
        ('false', bool, False),
        ('false', None, 'false'),
        ('hello', None, 'hello'),
        (123, None, 123),
    ])
    def test_convert(self, value, type, result):
        spec = Spec('name', type=type)
        assert spec.convert(value) == result

    # Test: convert incorrect values.
    @pytest.mark.parametrize('value,type', [
        ('hello', int),
        ('hello', bool),
    ])
    def test_convert_incorrect(self, value, type):
        spec = Spec('name', type=type)
        with pytest.raises(ValueError):
            spec.convert(value)

    # Test: convert help string to lines.
    def test_help_to_lines(self):
        spec = Spec('name', help='Single line.')
        assert spec.help_to_lines() == ['Single line.']

        spec.help = """
        Line 1
        Line 2
            Line 3
        """
        assert spec.help_to_lines() == ['Line 1', 'Line 2', '    Line 3']

    # Test: convert type to string representation.
    def test_type_to_string(self):
        spec = Spec('name')

        assert spec.type_to_string(None) == 'null'
        assert spec.type_to_string(bool) == 'yes/no'
        assert spec.type_to_string(int) == '<number>'
        assert spec.type_to_string(float) == '<number>'
        assert spec.type_to_string(str) == '<text>'

    # Test: add type info to text lines.
    def test_add_type_info(self):
        lines = []
        spec = Spec('name', type=int)
        spec.add_type_info(lines)
        assert lines == ['Value: <number>']

    # Test: Build text representation of spec.
    def test_to_lines(self):
        spec = Spec('name', help='line1\nline2', type=int)
        assert spec.to_lines() == ['line1', 'line2', 'Value: <number>']


# Test: MultiTypeSpec class.
class TestMultiTypeSpec:
    def test_construct(self):
        spec = MultiTypeSpec('name', 'help', (int, dict))
        assert spec.name == 'name'
        assert spec.help == 'help'
        assert spec.type == (int, dict)

    # Test: do_validate().
    @pytest.mark.parametrize('value,type,valid', [
        (123, (int,), True),
        (123, (None, int,), True),
        ('123', (None, int,), False),
        (None, (None, int,), True),
        ('123', (str, int,), True),
        (False, (str, int, bool), True),
    ])
    def test_do_validate(self, value, type, valid):
        spec = MultiTypeSpec('name', type=type)
        assert spec.do_validate(value) == valid

    # Test: convert string to value with spec's type.
    @pytest.mark.parametrize('value,type,result', [
        (123, (int,), 123),
        ('123', (int,), 123),
        ('bla', (int, str), 'bla'),
        ('yes', (int, bool, str), True),
        ('no', (int, bool, str), False),
    ])
    def test_convert(self, value, type, result):
        spec = MultiTypeSpec('name', type=type)
        assert spec.convert(value) == result

    # Test: convert incorrect values.
    @pytest.mark.parametrize('value,type', [
        ('hello', (bool, int)),
        ('12s', (bool, int)),
    ])
    def test_convert_incorrect(self, value, type):
        spec = MultiTypeSpec('name', type=type)
        with pytest.raises(ValueError):
            spec.convert(value)

    # Test: add type info to text lines.
    def test_add_type_info(self):
        lines = []
        spec = MultiTypeSpec('name', type=(None, int, bool, str))
        spec.add_type_info(lines)
        assert lines == ['Value: null, <number>, yes/no, <text>']


# Test: ChoiceSpec class.
class TestChoiceSpec:
    def test_construct(self):
        spec = ChoiceSpec('name', 'help', (1, 2))
        assert spec.name == 'name'
        assert spec.help == 'help'
        assert spec.type == (1, 2)

    # Test: do_validate().
    @pytest.mark.parametrize('value,type,valid', [
        ('a', ('a', 'b c'), True),
        ('b c', ('a', 'b c'), True),
        ('123', ('a', 'b c'), False),
    ])
    def test_do_validate(self, value, type, valid):
        spec = ChoiceSpec('name', type=type)
        assert spec.do_validate(value) == valid

    # Test: convert string to value with spec's type.
    @pytest.mark.parametrize('value,type,result', [
        ('a', ('a', 'b c'), 'a'),
        ('b c', ('a', 'b c'), 'b c'),
    ])
    def test_convert(self, value, type, result):
        spec = ChoiceSpec('name', type=type)
        assert spec.convert(value) == result

    # Test: convert incorrect values.
    @pytest.mark.parametrize('value,type', [
        ('v', ('a', 'b')),
        (1, ('a', 'b')),
    ])
    def test_convert_incorrect(self, value, type):
        spec = ChoiceSpec('name', type=type)
        with pytest.raises(ValueError):
            spec.convert(value)

    # Test: add type info to text lines.
    def test_add_type_info(self):
        lines = []
        spec = ChoiceSpec('name', type=('a', 'b'))
        spec.add_type_info(lines)
        assert lines == ["Value: ('a', 'b')"]


# Test: choice type C.
class TestC:
    # Test: construction.
    def test_construct(self):
        c = C(1, 2, 3)
        assert c.values == (1, 2, 3)


# Test: SettingsBuilder class.
# TODO: add more tests.
class TestSettingsBuilder:
    # Test: construction.
    def test_construct(self):
        logger = Mock()
        c = SettingsBuilder(logger)
        assert c.settings == {}
        assert c.specs == {}
        assert c.logger is logger

    def test_add_specs(self):
        c = SettingsBuilder(Mock())

        c.add_specs((
            ('help', 'intvar', 1),
            ('help 2', 'bool_or_null', True, (None, bool)),
            ('help 3', 'choice', 'two', C('one', 'two')),
        ), c.settings)

        assert c.settings == {
            'intvar': 1,
            'bool_or_null': True,
            'choice': 'two'
        }

        assert sorted(c.specs.keys()) == ['bool_or_null', 'choice', 'intvar']

        spec = c.specs['intvar']
        assert spec.name == 'intvar'
        assert spec.help == 'help'
        assert spec.type == int

        spec = c.specs['bool_or_null']
        assert spec.name == 'bool_or_null'
        assert spec.help == 'help 2'
        assert spec.type == (None, bool)

        spec = c.specs['choice']
        assert spec.name == 'choice'
        assert spec.help == 'help 3'
        assert spec.type == ('one', 'two')

    def test_add_specs_recursive(self):
        c = SettingsBuilder(Mock())

        c.add_specs((
            ('help', 'intvar', 1),
            ('help 1', 'dictvar', (
                ('help 2', 'bool_or_null', True, (None, bool)),
                ('help 3', 'choice', 'two', C('one', 'two')),
            )),
        ), c.settings)

        assert c.settings == {
            'intvar': 1,
            'dictvar': {
                'bool_or_null': True,
                'choice': 'two'
            }
        }

        assert sorted(c.specs.keys()) == ['bool_or_null', 'choice', 'dictvar',
                                          'intvar']

        spec = c.specs['intvar']
        assert spec.name == 'intvar'
        assert spec.help == 'help'
        assert spec.type == int

        spec = c.specs['bool_or_null']
        assert spec.name == 'bool_or_null'
        assert spec.help == 'help 2'
        assert spec.type == (None, bool)

        spec = c.specs['choice']
        assert spec.name == 'choice'
        assert spec.help == 'help 3'
        assert spec.type == ('one', 'two')

        spec = c.specs['dictvar']
        assert spec.name == 'dictvar'
        assert spec.help == 'help 1'
        assert spec.type is dict

    def test_collect(self):
        spec1 = Mock(settings_spec_help=None)
        spec1.settings_section = 'one'
        spec1.settings_spec = (
            ('help', 'intvar', 1),
            ('help 2', 'bool_or_null', True, (None, bool)),
            ('help 3', 'choice', 'two', C('one', 'two')),
        )

        spec2 = Mock(settings_spec_help=None, settings_spec_nested=())
        spec2.settings_section = 'two'
        spec2.settings_spec = (
            ('help 4', 'a', 1),
            ('help 5', 'c', '1', C('1', '2')),
        )

        spec1.settings_spec_nested = (spec2,)

        c = SettingsBuilder(Mock())
        c.collect(spec1)

        assert c.settings == {
            'one': {
                'intvar': 1,
                'bool_or_null': True,
                'choice': 'two',
                'two': {
                    'a': 1,
                    'c': '1',
                }
            }
        }

        assert sorted(c.specs.keys()) == ['a', 'bool_or_null', 'c', 'choice',
                                          'intvar', 'one', 'two']

        spec = c.specs['one']
        assert spec.name == 'one'
        assert spec.help is None
        assert spec.type is None

        spec = c.specs['intvar']
        assert spec.name == 'intvar'
        assert spec.help == 'help'
        assert spec.type == int

        spec = c.specs['bool_or_null']
        assert spec.name == 'bool_or_null'
        assert spec.help == 'help 2'
        assert spec.type == (None, bool)

        spec = c.specs['choice']
        assert spec.name == 'choice'
        assert spec.help == 'help 3'
        assert spec.type == ('one', 'two')

        spec = c.specs['two']
        assert spec.name == 'two'
        assert spec.help is None
        assert spec.type is None

        spec = c.specs['a']
        assert spec.name == 'a'
        assert spec.help == 'help 4'
        assert spec.type == int

        spec = c.specs['c']
        assert spec.name == 'c'
        assert spec.help == 'help 5'
        assert spec.type == ('1', '2')

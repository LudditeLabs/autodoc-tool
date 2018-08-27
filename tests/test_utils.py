import pytest
import os.path as op
from unittest.mock import Mock, call
import yaml
from autodoc.utils import merge_recursive, InheritDict


# Tet: merge_recursive()
class TestMergeRecursive:
    # Test: merge
    @pytest.mark.parametrize('data', [
        {
            'src': dict(a=1, b=2),
            'merge': dict(a=10, c=20),
            'result': dict(a=10, b=2, c=20)
        },
        {
            'src': dict(a=1, b=2, c=dict(x=1, y=3)),
            'merge': dict(a=10, c=20),
            'result': dict(a=10, b=2, c=20)
        },
        {
            'src': dict(a=1, b=2, c=20),
            'merge': dict(a=10, c=dict(x=1, y=3)),
            'result': dict(a=10, b=2, c=dict(x=1, y=3))
        },
        {
            'src': dict(a=1, b=2, c=dict(x=1, y=3)),
            'merge': dict(a=10, c=dict(x=10, z=4)),
            'result': dict(a=10, b=2, c=dict(x=10, y=3, z=4))
        },
        {
            'src': {
                'a': 1,
                'b': {
                    'n1': {
                        'm': 2,
                        'x': {'zz': 12}
                    }
                },
                'c': {'x': 1, 'y': 3}
            },
            'merge': {
                'a': 10,
                'b': {
                    'n1': {
                        'x': {'zy': 7}
                    },
                    'n2': {'x': 10, 'z': 4}
                }
            },
            'result': {
                'a': 10,
                'b': {
                    'n1': {
                        'm': 2,
                        'x': {'zz': 12, 'zy': 7}
                    },
                    'n2': {'x': 10, 'z': 4}
                },
                'c': {'x': 1, 'y': 3}
            }
        },
    ])
    def test_merge(self, data):
        merge_recursive(data['src'], data['merge'])
        assert data['src'] == data['result']

    # Test: cal callback function
    def test_callback(self):
        src = dict(a=1, b=2, c=20, d=dict(x=10))
        merge = dict(a=10, c=dict(x=1, y=3), d=dict(e=11, f=8))

        callback = Mock()
        merge_recursive(src, merge, callback)

        assert src == dict(a=10, b=2, c=dict(x=1, y=3), d=dict(x=10, e=11, f=8))
        assert sorted(callback.mock_calls, key=lambda x: x[1][0]) == [
            call('a', 10),
            call('c', dict(x=1, y=3)),
            call('d', dict(e=11, f=8)),
            call('e', 11),
            call('f', 8),
        ]


# Test: InheritDict.
class TestInheritDict:
    # Test: construct from a dict.
    def test_construct(self):
        data = {'a': 1, 'b': True, 'c': 'text', 'd': [1, '3']}
        cfg = InheritDict(data)
        assert cfg._data is data
        assert cfg._cache == {}
        assert cfg._name is None
        assert cfg._parent is None

    # Test: one dict is nested.
    def test_construct_nested(self):
        cfg = InheritDict({
            'a': 1,
            'b': True,
            'c': 'text',
            'd': {
                'a': 2,
                'e': {
                    'one': 1
                }
            },
            'f': {
                'e': 3
            }
        })

        # Make sure nested dict is wrapped with InheritDict.
        d = cfg._data.pop('d')
        assert isinstance(d, InheritDict)
        assert d._name == 'd'
        assert d._parent is cfg

        e = d._data.pop('e')
        assert isinstance(e, InheritDict)
        assert e._name == 'e'
        assert e._parent is d
        assert e._data == {'one': 1}

        assert d._data == {'a': 2}

        f = cfg._data.pop('f')
        assert isinstance(f, InheritDict)
        assert f._name == 'f'
        assert f._parent is cfg
        assert f._data == {'e': 3}

        assert cfg._data == {'a': 1, 'b': True, 'c': 'text'}


# Test: InheritDict lookup algo.
class TestInheritDictLookup:
    def setup_method(self, m):
        self.data = InheritDict(yaml.load("""
        line_width: 80
        indent_global: 0
        indent: 4

        py:
            style: google
            line_width: 70

            rst:
                margin: 2
                opt_margin: False
                shorten_inline: True

            google:
                line_width: 50

            fake:
                rst:
                    nested:
                        one: 3

                opts:
                    nested:
                        one: 1

        cpp:
            opts:
                nested:
                    xx: 'yy'
        """))

    # Test: make sure cache is used before other ways.
    def test_use_cache(self):
        self.data._cache['fake'] = '12'
        assert self.data['fake'] == '12'

    # Test: lookup in top level.
    def test_top_level(self):
        assert self.data._cache == {}
        assert self.data['line_width'] == 80
        assert self.data._cache == {'line_width': 80}  # Cache must be updated.

    # Test: lookup non existent key in top level.
    def test_top_level_fail(self):
        with pytest.raises(KeyError) as e:
            assert self.data['fake']
        assert str(e.value) == "'fake'"

    # Test: lookup in nested dict.
    def test_level1(self):
        py = self.data['py']
        assert py['style'] == 'google'
        assert py['line_width'] == 70
        assert py['indent'] == 4

        # NOTE: parent also caches missing fields.

        assert self.data._cache == {'py': py, 'indent': 4}
        assert py._cache == {'line_width': 70, 'indent': 4, 'style': 'google'}

    # Test: lookup in nested dict.
    def test_level2(self):
        py = self.data['py']
        rst = py['rst']
        assert rst['style'] == 'google'
        assert rst['line_width'] == 70
        assert rst['indent'] == 4
        assert rst['margin'] == 2

        # NOTE: parents also cache missing fields.

        assert rst._cache == {'line_width': 70, 'indent': 4, 'style': 'google',
                              'margin': 2}
        assert py._cache == {'line_width': 70, 'indent': 4, 'style': 'google',
                             'rst': rst}
        assert self.data._cache == {'py': py, 'indent': 4}

        # NOTE: this one is recursive since gets self value from the parent.
        assert rst['rst'] is rst

    # Test: lookup various keys.
    def test_multilevel(self):
        assert self.data['line_width'] == 80
        assert self.data['py']['line_width'] == 70
        assert self.data['py']['rst']['margin'] == 2
        assert self.data['py']['fake']['opts']['nested']['one'] == 1

    # Test: get_by_path()
    def test_get_by_path(self):
        assert self.data.get_by_path('line_width') == 80
        assert self.data.get_by_path('py.line_width') == 70
        assert self.data.get_by_path('py.rst.margin') == 2
        assert self.data.get_by_path('py.fake.opts.nested.one') == 1

    # Test: missing keys.
    @pytest.mark.parametrize('key,msgkey', [
        ('xxx', 'xxx'),
        ('fakepy.xxx', 'fakepy'),
        ('py.xxx', 'xxx'),
        ('py.rst.xxx', 'xxx'),
        ('py.fake.rst.nested.xxx', 'xxx')
    ])
    def test_missing(self, key, msgkey):
        with pytest.raises(KeyError) as e:
            x = self.data.get_by_path(key)
        assert str(e.value) == "'%s'" % msgkey

    # Test: get()
    def test_get(self):
        assert self.data.get('line_width') == 80
        assert self.data['py'].get('line_width') == 70
        assert self.data['py'].get('indent') == 4
        assert self.data['py'].get('xxxx') is None
        assert self.data['py'].get('xxxx', 1) == 1

    # Test: __str__()
    def test_str(self):
        assert str(self.data) == '<InheritDict>'
        assert str(self.data['py']) == '<InheritDict:py>'
        assert str(self.data['py']['google']) == '<InheritDict:google>'

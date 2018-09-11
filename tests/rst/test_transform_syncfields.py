from __future__ import absolute_import
import logging
from autodoc.contentdb import Arg
from autodoc.python.rst.transforms.collect_fields import CollectInfoFields
from autodoc.python.rst.transforms.sync_params import SyncParametersWithSpec
from autodoc.report import Codes

# These param will be loaded by the fixtures (assert_py_doc, parse_py_doc).
docstring_transforms = [CollectInfoFields, SyncParametersWithSpec]


class TestSyncParams:
    def test_no_params(self, parse_py_doc):
        env = parse_py_doc(
            # def test_func(name, type)
            args=(Arg('param1', None), Arg('param2', ['int'])),
            text="""
            This is an ordinary paragraph.

            :except RuntimeError:

            Ut enim ad minim veniam, quis nostrud.
            """
        )

        doc = env['definition'].doc_block.document
        assert hasattr(doc, 'field_sections')

        section = doc.field_sections.get('params')
        assert section is not None
        assert len(section) == 2

        param = section[0]
        assert param.get('name') == 'param1'
        assert param.get('type') is None
        assert param.get('orig_field_tag') == 'param'
        assert len(param) == 1
        assert len(param[0]) == 0

        param = section[1]
        assert param.get('name') == 'param2'
        assert param.get('type') == ['int']
        assert param.get('orig_field_tag') == 'param'
        assert len(param) == 1
        assert len(param[0]) == 0

    def test_with_params(self, parse_py_doc):
        args = (Arg('with_separate_type', None),
                Arg('with_type', ['str']),
                Arg('no_type', None),
                Arg('new_PARAM', None),
                Arg('type_wrong_place', ['str', 'int']))

        env = parse_py_doc(
            args=args,
            text="""
            This is an ordinary paragraph.

            :parameter:
            :type type_wrong_place: xxx
            :param no_type: No type.
            :param type_wrong_place: Wrong place.
            :param str with_type: With type.
            :parameter with_separate_type: With separate type.
            :type with_separate_type: integer or None
            :type with_separate_type: string
            :type non_exist: str
            :parameter to_remove: This one will be removed.

            This is a paragraph after the field list.
            """
        )

        doc = env['definition'].doc_block.document
        assert hasattr(doc, 'field_sections')

        section = doc.field_sections.get('params')
        assert section is not None
        assert len(section) == 5

        param = section[0]
        assert param.get('name') == 'with_separate_type'
        assert param.get('type') == ['integer or None', 'string']
        assert param.get('orig_field_tag') == 'parameter'
        assert len(param) == 1
        assert len(param[0]) == 1
        assert param[0][0].astext() == 'With separate type.'

        param = section[1]
        assert param.get('name') == 'with_type'
        assert param.get('type') == ['str']
        assert param.get('orig_field_tag') == 'param'
        assert len(param) == 1
        assert len(param[0]) == 1
        assert param[0][0].astext() == 'With type.'

        param = section[2]
        assert param.get('name') == 'no_type'
        assert param.get('type') is None
        assert param.get('orig_field_tag') == 'param'
        assert len(param) == 1
        assert len(param[0]) == 1
        assert param[0][0].astext() == 'No type.'

        param = section[3]
        assert param.get('name') == 'new_PARAM'
        assert param.get('type') is None
        assert param.get('orig_field_tag') == 'param'
        assert len(param) == 1
        assert len(param[0]) == 0

        param = section[4]
        assert param.get('name') == 'type_wrong_place'
        assert param.get('type') == ['str', 'int']
        assert param.get('orig_field_tag') == 'param'
        assert len(param) == 1
        assert len(param[0]) == 1
        assert param[0][0].astext() == 'Wrong place.'

    def test_with_missing_params(self, parse_py_doc):
        args = (Arg('with_separate_type', None),
                Arg('with_type', ['str']),
                Arg('no_type', None),
                Arg('new_PARAM', None),
                Arg('type_wrong_place', ['str', 'int']))

        env = parse_py_doc(
            args=args,
            text="""
            This is an ordinary paragraph.

            This is a paragraph after the field list.
            """
        )

        doc = env['definition'].doc_block.document
        assert hasattr(doc, 'field_sections')

        section = doc.field_sections.get('params')
        assert section is not None
        assert len(section) == 5

        param = section[0]
        assert param.get('name') == 'with_separate_type'
        assert param.get('type') is None
        assert param.get('orig_field_tag') == 'param'
        assert len(param) == 1
        assert len(param[0]) == 0

        param = section[1]
        assert param.get('name') == 'with_type'
        assert param.get('type') == ['str']
        assert param.get('orig_field_tag') == 'param'
        assert len(param) == 1
        assert len(param[0]) == 0

        param = section[2]
        assert param.get('name') == 'no_type'
        assert param.get('type') is None
        assert param.get('orig_field_tag') == 'param'
        assert len(param) == 1
        assert len(param[0]) == 0

        param = section[3]
        assert param.get('name') == 'new_PARAM'
        assert param.get('type') is None
        assert param.get('orig_field_tag') == 'param'
        assert len(param) == 1
        assert len(param[0]) == 0

        param = section[4]
        assert param.get('name') == 'type_wrong_place'
        assert param.get('type') == ['str', 'int']
        assert param.get('orig_field_tag') == 'param'
        assert len(param) == 1
        assert len(param[0]) == 0

    def test_report(self, parse_py_doc):
        args = (Arg('with_separate_type', None),
                Arg('with_type', ['str']),
                Arg('no_type', None),
                Arg('new_PARAM', None),
                Arg('type_wrong_place', ['str', 'int']))

        env = parse_py_doc(
            args=args,
            text="""
            This is an ordinary paragraph.

            :param no_type: No type.
            :param type_wrong_place: Wrong place.
            :type type_wrong_place: xxx
            :param str with_type: With type.
            :parameter with_separate_type: With separate type.
            :type with_separate_type: integer or None
            :type with_separate_type: string
            :parameter to_remove: This one will be removed.

            This is a paragraph after the field list.
            """
        )

        doc = env['definition'].doc_block.document
        assert hasattr(doc, 'field_sections')

        report = env.get('reporter').report
        assert isinstance(report, list)
        assert len(report) == 7

        for i, item in enumerate(report):
            assert len(item) == 8, 'Report at %d.' % i

        # Note: analysis proceeds in the order of args,
        # so errors will appear in the same order.

        path, domain, line, col, ref_name, level, code, msg = report[0]
        assert path == '<string>'
        assert domain == 'python'
        assert line == 0
        assert col == 0
        assert ref_name == 'test_func'
        assert level == logging.INFO
        assert code == Codes.INCORRECT
        assert msg == 'Parameter order is incorrect [with_separate_type]'

        path, domain, line, col, ref_name, level, code, msg = report[1]
        assert path == '<string>'
        assert domain == 'python'
        assert line == 0
        assert col == 0
        assert ref_name == 'test_func'
        assert level == logging.INFO
        assert code == Codes.INCORRECT
        assert msg == 'Parameter order is incorrect [with_type]'

        path, domain, line, col, ref_name, level, code, msg = report[2]
        assert path == '<string>'
        assert domain == 'python'
        assert line == 0
        assert col == 0
        assert ref_name == 'test_func'
        assert level == logging.INFO
        assert code == Codes.INCORRECT
        assert msg == 'Parameter order is incorrect [no_type]'

        path, domain, line, col, ref_name, level, code, msg = report[3]
        assert path == '<string>'
        assert domain == 'python'
        assert line == 0
        assert col == 0
        assert ref_name == 'test_func'
        assert level == logging.INFO
        assert code == Codes.MISSING
        assert msg == 'Missing parameter [new_PARAM]'

        path, domain, line, col, ref_name, level, code, msg = report[4]
        assert path == '<string>'
        assert domain == 'python'
        assert line == 0
        assert col == 0
        assert ref_name == 'test_func'
        assert level == logging.INFO
        assert code == Codes.MISMATCH
        assert msg == 'Parameter type is different [type_wrong_place]'

        path, domain, line, col, ref_name, level, code, msg = report[5]
        assert path == '<string>'
        assert domain == 'python'
        assert line == 0
        assert col == 0
        assert ref_name == 'test_func'
        assert level == logging.INFO
        assert code == Codes.INCORRECT
        assert msg == 'Parameter order is incorrect [type_wrong_place]'

        path, domain, line, col, ref_name, level, code, msg = report[6]
        assert path == '<string>'
        assert domain == 'python'
        assert line == 0
        assert col == 0
        assert ref_name == 'test_func'
        assert level == logging.INFO
        assert code == Codes.UNKNOWN
        assert msg == 'Unknown parameter [to_remove]'

    # Test: Skip first arg for method and class methods
    def test_method(self, parse_py_doc):
        args = (Arg('self', None), Arg('with_type', ['str']))

        env = parse_py_doc(
            args=args,
            compound_kind='class',  # Use method instead of function.
            text="""
            This is an ordinary paragraph.

            :param str with_type: With type.

            This is a paragraph after the field list.
            """
        )

        doc = env['definition'].doc_block.document
        assert hasattr(doc, 'field_sections')

        section = doc.field_sections.get('params')
        assert section is not None
        assert len(section) == 1

        param = section[0]
        assert param.get('name') == 'with_type'
        assert param.get('type') == ['str']

        report = env.get('reporter').report
        assert isinstance(report, list)
        assert not len(report)

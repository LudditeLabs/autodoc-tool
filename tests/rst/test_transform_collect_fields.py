import logging
from autodoc.python.rst.transforms.collect_fields import CollectInfoFields
from autodoc.report import Codes

# These param will be loaded by the fixtures (assert_py_doc, parse_py_doc).
docstring_transforms = [CollectInfoFields]


# Test: convert :param: and :type: to <param_field> and move them to the
# doc parts.
class TestParamField:
    # Test: parameters and their types.
    def test_fields(self, parse_py_doc):
        env = parse_py_doc(
            text="""
            This is an ordinary paragraph.

            :parameter:
            :type type_wrong_place: xxx
            :param no_type: Lorem ipsum dolor sit amet.
            :param type_wrong_place: 123
            :param str with_type: Do eiusmod tempor incididunt ut labore
                et dolore magna aliqua.
            :parameter with_separate_type: Ut enim ad minim veniam,
                quis nostrud exercitation.

                Paragraph 2.
            :type with_separate_type: integer or None
            :type with_separate_type: string
            :type non_exist: str

            This is a paragraph after the field list.

            .. seealso:: Another function.

            .. note:: Lorem ipsum dolor sit amet, consectetur adipiscing elit.
            """
        )

        doc = env['definition'].doc_block.document
        assert hasattr(doc, 'field_sections')

        section = doc.field_sections.get('params')
        assert section is not None
        assert len(section) == 4

        # Parameter no_type.
        param = section[0]
        assert param.get('name') == 'no_type'
        assert param.get('type') is None
        assert param.get('orig_field_tag') == 'param'
        assert len(param) == 1
        assert len(param[0]) == 1
        assert param[0][0].astext() == 'Lorem ipsum dolor sit amet.'

        # Parameter type_wrong_place.
        param = section[1]
        assert param.get('name') == 'type_wrong_place'
        assert param.get('type') == ['xxx']
        assert param.get('orig_field_tag') == 'param'
        assert len(param) == 1
        assert len(param[0]) == 1

        # Parameter with_type.
        param = section[2]
        assert param.get('name') == 'with_type'
        assert param.get('type') == ['str']
        assert param.get('orig_field_tag') == 'param'
        assert len(param) == 1
        assert len(param[0]) == 1

        # Parameter with_separate_type.
        param = section[3]
        assert param.get('name') == 'with_separate_type'
        assert param.get('type') == ['integer or None', 'string']
        assert param.get('orig_field_tag') == 'parameter'
        assert len(param) == 1
        assert len(param[0]) == 2

    # Test: report messages.
    def test_report(self, parse_py_doc):
        env = parse_py_doc(
            add_report=True,
            text="""
            This is an ordinary paragraph.

            :parameter:
            :type type_wrong_place: xxx
            :param no_type: Lorem ipsum dolor sit amet.
            :param no_type: Lorem ipsum dolor sit amet.
            :param type_wrong_place: 123
            :param str with_type: Do eiusmod tempor incididunt ut labore
                et dolore magna aliqua.
            :parameter with_separate_type: Ut enim ad minim veniam,
                quis nostrud exercitation.

                Paragraph 2.
            :type with_separate_type: integer or None
            :type with_separate_type: string
            :type non_exist: str
            :type: str
            :type with_separate_type: yyy

            :param xxx: 123
            :type xxx: Do eiusmod tempor incididunt ut labore
                et dolore magna aliqua.
            """
        )
        doc = env['definition'].doc_block.document
        assert hasattr(doc, 'field_sections')

        report = env.get('reporter').report
        assert isinstance(report, list)
        assert len(report) == 5

        for i, item in enumerate(report):
            assert len(item) == 8, 'Report at %d.' % i

        report.sort()

        path, domain, line, col, func_name, level, code, msg = report[0]
        assert path == '<string>'   # conftest setup this.
        assert domain == 'python'

        # NOTE: currently we drop position in the docstring
        # and use position of the ref (function, class).
        assert line == 0
        assert col == 0

        assert func_name == 'test_func'
        assert level == logging.INFO
        assert code == Codes.COMPLEX
        assert msg == 'Type specification is too complex [:type xxx:]'

        path, domain, line, col, func_name, level, code, msg = report[1]
        assert path == '<string>'
        assert domain == 'python'
        assert line == 0
        assert col == 0
        assert func_name == 'test_func'
        assert level == logging.INFO
        assert code == Codes.DUPLICATE
        assert msg == 'Duplicate field [:param no_type:]'

        # This check happens before line 16 checks.
        path, domain, line, col, func_name, level, code, msg = report[2]
        assert path == '<string>'
        assert domain == 'python'
        assert line == 0
        assert col == 0
        assert func_name == 'test_func'
        assert level == logging.INFO
        assert code == Codes.INCORRECT
        assert msg == 'Incorrect signature [:parameter:]'

        path, domain, line, col, func_name, level, code, msg = report[3]
        assert path == '<string>'
        assert domain == 'python'
        assert line == 0
        assert col == 0
        assert func_name == 'test_func'
        assert level == logging.INFO
        assert code == Codes.INCORRECT
        assert msg == 'Incorrect signature [:type:]'

        path, domain, line, col, func_name, level, code, msg = report[4]
        assert path == '<string>'
        assert domain == 'python'
        assert line == 0
        assert col == 0
        assert func_name == 'test_func'
        assert level == logging.INFO
        assert code == Codes.UNKNOWN
        assert msg == 'Type for unknown parameter [non_exist]'

    # Test: remove detected and invalid fields
    def test_remove(self, assert_py_doc):
        assert_py_doc(
            text="""
            This is an ordinary paragraph.

            :parameter:
            :type type_wrong_place: xxx
            :param no_type: Lorem ipsum dolor sit amet.
            :param no_type: Lorem ipsum dolor sit amet.
            :param type_wrong_place: 123
            :param str with_type: Do eiusmod tempor incididunt ut labore
                et dolore magna aliqua.
            :parameter with_separate_type: Ut enim ad minim veniam,
                quis nostrud exercitation.

                Paragraph 2.
            :type with_separate_type: integer or None
            :type non_exist: str
            :type: str
            :type with_separate_type: yyy

            :param xxx: 123
            :type xxx: Do eiusmod tempor incididunt ut labore
                et dolore magna aliqua.
            """,
            expected="""This is an ordinary paragraph."""
        )


# Test: convert :keyword: and :kwtype: to <keyword_field> and move them to the
# doc parts.
class TestKwField:
    # Test: parameters and their types.
    def test_fields(self, parse_py_doc):
        env = parse_py_doc(
            text="""
            This is an ordinary paragraph.

            :keyword:
            :kwtype type_wrong_place: xxx
            :keyword no_type: Lorem ipsum dolor sit amet.
            :keyword type_wrong_place: 123
            :keyword str with_type: Do eiusmod tempor incididunt ut labore
                et dolore magna aliqua.
            :keyword with_separate_type: Ut enim ad minim veniam,
                quis nostrud exercitation.

                Paragraph 2.
            :kwtype with_separate_type: integer or None
            :kwtype with_separate_type: string
            :kwtype non_exist: str

            This is a paragraph after the field list.
            """
        )

        doc = env['definition'].doc_block.document
        assert hasattr(doc, 'field_sections')

        section = doc.field_sections.get('keyword')
        assert section is not None
        assert len(section) == 4

        # Parameter no_type.
        param = section[0]
        assert param.get('name') == 'no_type'
        assert param.get('type') is None
        assert param.get('orig_field_tag') == 'keyword'
        assert len(param) == 1
        assert len(param[0]) == 1
        assert param[0][0].astext() == 'Lorem ipsum dolor sit amet.'

        # Parameter type_wrong_place.
        param = section[1]
        assert param.get('name') == 'type_wrong_place'
        assert param.get('type') == ['xxx']
        assert param.get('orig_field_tag') == 'keyword'
        assert len(param) == 1
        assert len(param[0]) == 1

        # Parameter with_type.
        param = section[2]
        assert param.get('name') == 'with_type'
        assert param.get('type') == ['str']
        assert param.get('orig_field_tag') == 'keyword'
        assert len(param) == 1
        assert len(param[0]) == 1

        # Parameter with_separate_type.
        param = section[3]
        assert param.get('name') == 'with_separate_type'
        assert param.get('type') == ['integer or None', 'string']
        assert param.get('orig_field_tag') == 'keyword'
        assert len(param) == 1
        assert len(param[0]) == 2

    # Test: report messages.
    def test_report(self, parse_py_doc):
        env = parse_py_doc(
            add_report=True,
            text="""
            This is an ordinary paragraph.

            :keyword:
            :kwtype type_wrong_place: xxx
            :keyword no_type: Lorem ipsum dolor sit amet.
            :keyword no_type: Lorem ipsum dolor sit amet.
            :keyword type_wrong_place: 123
            :keyword str with_type: Do eiusmod tempor incididunt ut labore
                et dolore magna aliqua.
            :keyword with_separate_type: Ut enim ad minim veniam,
                quis nostrud exercitation.

                Paragraph 2.
            :kwtype with_separate_type: integer or None
            :kwtype with_separate_type: string
            :kwtype non_exist: str
            :kwtype: str
            :kwtype with_separate_type: yyy

            :keyword xxx: 123
            :kwtype xxx: Do eiusmod tempor incididunt ut labore
                et dolore magna aliqua.
            """
        )
        doc = env['definition'].doc_block.document
        assert hasattr(doc, 'field_sections')

        report = env.get('reporter').report
        assert isinstance(report, list)
        assert len(report) == 5

        for i, item in enumerate(report):
            assert len(item) == 8, 'Report at %d.' % i

        report.sort()

        path, domain, line, col, ref_name, level, code, msg = report[0]
        assert path == '<string>'   # conftest setup this.
        assert domain == 'python'

        # NOTE: currently we drop position in the docstring
        # and use position of the ref (function, class).
        assert line == 0
        assert col == 0

        assert ref_name == 'test_func'
        assert level == logging.INFO
        assert code == Codes.COMPLEX
        assert msg == 'Type specification is too complex [:kwtype xxx:]'

        path, domain, line, col, ref_name, level, code, msg = report[1]
        assert path == '<string>'
        assert domain == 'python'
        assert line == 0
        assert col == 0
        assert ref_name == 'test_func'
        assert level == logging.INFO
        assert code == Codes.DUPLICATE
        assert msg == 'Duplicate field [:keyword no_type:]'

        # This check happens before line 16 checks.
        path, domain, line, col, ref_name, level, code, msg = report[2]
        assert path == '<string>'
        assert domain == 'python'
        assert line == 0
        assert col == 0
        assert ref_name == 'test_func'
        assert level == logging.INFO
        assert code == Codes.INCORRECT
        assert msg == 'Incorrect signature [:keyword:]'

        path, domain, line, col, ref_name, level, code, msg = report[3]
        assert path == '<string>'
        assert domain == 'python'
        assert line == 0
        assert col == 0
        assert ref_name == 'test_func'
        assert level == logging.INFO
        assert code == Codes.INCORRECT
        assert msg == 'Incorrect signature [:kwtype:]'

        path, domain, line, col, ref_name, level, code, msg = report[4]
        assert path == '<string>'
        assert domain == 'python'
        assert line == 0
        assert col == 0
        assert ref_name == 'test_func'
        assert level == logging.INFO
        assert code == Codes.UNKNOWN
        assert msg == 'Type for unknown parameter [non_exist]'

    # Test: remove detected and invalid fields
    def test_remove(self, assert_py_doc):
        assert_py_doc(
            text="""
            This is an ordinary paragraph.

            :keyword:
            :kwtype type_wrong_place: xxx
            :keyword no_type: Lorem ipsum dolor sit amet.
            :keyword no_type: Lorem ipsum dolor sit amet.
            :keyword type_wrong_place: 123
            :keyword str with_type: Do eiusmod tempor incididunt ut labore
                et dolore magna aliqua.
            :keyword with_separate_type: Ut enim ad minim veniam,
                quis nostrud exercitation.

                Paragraph 2.
            :kwtype with_separate_type: integer or None
            :kwtype with_separate_type: string
            :kwtype non_exist: str
            :kwtype: str
            :kwtype with_separate_type: yyy

            :keyword xxx: 123
            :kwtype xxx: Do eiusmod tempor incididunt ut labore
                et dolore magna aliqua.
            """,
            expected="""This is an ordinary paragraph."""
        )


# Test: convert :return: and :rtype: to <returns_field> and move them to the
# doc parts.
class TestReturnField:
    def test_fields(self, parse_py_doc):
        env = parse_py_doc(
            text="""
            This is an ordinary paragraph.

            :return bla bla: Hz
            :returns: the message id 1
            :return: the message id 2
            :rtype: int
            :rtype: char

            Ut enim ad minim veniam, quis nostrud.
            """
        )

        doc = env['definition'].doc_block.document
        assert hasattr(doc, 'field_sections')

        section = doc.field_sections.get('returns')
        assert section is not None
        assert len(section) == 3

        ret = section[0]
        assert ret.get('type') is None
        assert ret.get('orig_field_tag') == 'returns'
        assert len(ret) == 1
        assert len(ret[0]) == 1
        assert ret[0][0].astext() == 'the message id 1'

        ret = section[1]
        assert ret.get('type') == ['int']
        assert ret.get('orig_field_tag') == 'return'
        assert len(ret) == 1
        assert len(ret[0]) == 1
        assert ret[0][0].astext() == 'the message id 2'

        ret = section[2]
        assert ret.get('type') == ['char']
        assert ret.get('orig_field_tag') == 'returns'
        assert len(ret) == 1
        assert len(ret[0]) == 0

    # Test: report messages.
    def test_report(self, parse_py_doc):
        env = parse_py_doc(
            add_report=True,
            text="""
            This is an ordinary paragraph.

            :return bla bla: Hz
            :return: the message id 2
            :return:
            :rtype: int
            :rtype: char
            :rtype bla: char
            :rtype: Do eiusmod tempor incididunt ut labore
                et dolore magna aliqua.

            Ut enim ad minim veniam, quis nostrud.
            """
        )

        doc = env['definition'].doc_block.document
        assert hasattr(doc, 'field_sections')

        report = env.get('reporter').report
        assert isinstance(report, list)
        assert len(report) == 4

        for i, item in enumerate(report):
            assert len(item) == 8, 'Report at %d.' % i

        path, domain, line, col, ref_name, level, code, msg = report[0]
        assert path == '<string>'   # conftest setup this.
        assert domain == 'python'

        # NOTE: currently we drop position in the docstring
        # and use position of the ref (function, class).
        assert line == 0
        assert col == 0

        assert ref_name == 'test_func'
        assert level == logging.INFO
        assert code == Codes.INCORRECT
        assert msg == 'Incorrect signature [:return:]'

        path, domain, line, col, ref_name, level, code, msg = report[1]
        assert path == '<string>'
        assert domain == 'python'
        assert line == 0
        assert col == 0
        assert ref_name == 'test_func'
        assert level == logging.INFO
        assert code == Codes.EMPTY
        assert msg == 'Empty content [:return:]'

        path, domain, line, col, ref_name, level, code, msg = report[2]
        assert path == '<string>'
        assert domain == 'python'
        assert line == 0
        assert col == 0
        assert ref_name == 'test_func'
        assert level == logging.INFO
        assert code == Codes.INCORRECT
        assert msg == 'Incorrect signature [:rtype:]'

        path, domain, line, col, ref_name, level, code, msg = report[3]
        assert path == '<string>'
        assert domain == 'python'
        assert line == 0
        assert col == 0
        assert ref_name == 'test_func'
        assert level == logging.INFO
        assert code == Codes.COMPLEX
        assert msg == 'Type specification is too complex [:rtype:]'

    # Test: remove detected and invalid fields
    def test_remove(self, assert_py_doc):
        assert_py_doc(
            text="""
            This is an ordinary paragraph.

            :return bla bla: Hz
            :return: the message id 2
            :return:
            :rtype: int
            :rtype: char
            :rtype bla: char
            :rtype: Do eiusmod tempor incididunt ut labore
                et dolore magna aliqua.

            Ut enim ad minim veniam, quis nostrud.
            """,
            expected="""
            This is an ordinary paragraph.

            Ut enim ad minim veniam, quis nostrud.
            """
        )


# Test: convert :raises: rtype: to <raises_field> and move them to the
# doc parts.
class TestRaisesField:
    def test_fields(self, parse_py_doc):
        env = parse_py_doc(
            text="""
            This is an ordinary paragraph.

            :raises:
            :raises ValueError: if the message_body exceeds 160
            :raise TypeError: if the message_body is not a basestring
            :except RuntimeError:
            :exception RuntimeError2:

            Ut enim ad minim veniam, quis nostrud.
            """
        )

        doc = env['definition'].doc_block.document
        assert hasattr(doc, 'field_sections')

        section = doc.field_sections.get('raises')
        assert section is not None
        assert len(section) == 4

        node = section[0]
        assert node.get('type') == ['ValueError']
        assert node.get('orig_field_tag') == 'raises'
        assert len(node) == 1
        assert len(node[0]) == 1
        assert node[0][0].astext() == 'if the message_body exceeds 160'

        node = section[1]
        assert node.get('type') == ['TypeError']
        assert node.get('orig_field_tag') == 'raise'
        assert len(node) == 1
        assert len(node[0]) == 1
        assert node[0][0].astext() == 'if the message_body is not a basestring'

        node = section[2]
        assert node.get('type') == ['RuntimeError']
        assert node.get('orig_field_tag') == 'except'
        assert len(node) == 1
        assert len(node[0]) == 0

        node = section[3]
        assert node.get('type') == ['RuntimeError2']
        assert node.get('orig_field_tag') == 'exception'
        assert len(node) == 1
        assert len(node[0]) == 0

    def test_report(self, parse_py_doc):
        env = parse_py_doc(
            add_report=True,
            text="""
            This is an ordinary paragraph.

            :raises:
            :raises ValueError: if the message_body exceeds 160
            :raise TypeError: if the message_body is not a basestring
            :except RuntimeError:
            :exception RuntimeError2:

            Ut enim ad minim veniam, quis nostrud.
            """
        )

        doc = env['definition'].doc_block.document
        assert hasattr(doc, 'field_sections')

        report = env.get('reporter').report
        assert isinstance(report, list)
        assert len(report) == 2

        assert len(report[0]) == 8

        path, domain, line, col, ref_name, level, code, msg = report[0]
        assert path == '<string>'   # conftest setup this.
        assert domain == 'python'

        # NOTE: currently we drop position in the docstring
        # and use position of the ref (function, class).
        assert line == 0
        assert col == 0

        assert ref_name == 'test_func'
        assert level == logging.INFO
        assert code == Codes.MISSING
        assert msg == 'Type is missing [:raises:]'

        path, domain, line, col, ref_name, level, code, msg = report[1]
        assert path == '<string>'   # conftest setup this.
        assert domain == 'python'

        # NOTE: currently we drop position in the docstring
        # and use position of the ref (function, class).
        assert line == 0
        assert col == 0

        assert ref_name == 'test_func'
        assert level == logging.INFO
        assert code == Codes.MISSING
        assert msg == 'Description is missing [:raises:]'

    # Test: remove detected and invalid fields.
    def test_remove(self, assert_py_doc):
        assert_py_doc(
            text="""
            This is an ordinary paragraph.

            :raises:
            :raises ValueError: if the message_body exceeds 160
            :raise TypeError: if the message_body is not a basestring
            :except RuntimeError:
            :exception RuntimeError2:
            :one:

            Ut enim ad minim veniam, quis nostrud.
            """,
            expected="""
            This is an ordinary paragraph.

            :one:

            Ut enim ad minim veniam, quis nostrud.
            """
        )


# Test: convert :Yields: <yields_field> and move them to the doc parts.
class TestYieldsField:
    def test_fields(self, parse_py_doc):
        env = parse_py_doc(
            text="""
            This is an ordinary paragraph.

            :Yields: Quis nostrud exercitation ullamco. In voluptate velit esse
                     cillum dolore eu fugiat nulla.
                     
                     Ut enim ad minim veniam.

            :Yields: 123
            :Yields:

            Ut enim ad minim veniam, quis nostrud.
            """
        )

        doc = env['definition'].doc_block.document
        assert hasattr(doc, 'field_sections')

        section = doc.field_sections.get('yields')
        assert section is not None
        # NOTE: empty :Yields: will be dropped.
        assert len(section) == 2

        node = section[0]
        assert node.get('orig_field_tag') == 'Yields'
        assert len(node) == 1
        assert len(node[0]) == 2
        assert node[0].astext() == ('Quis nostrud exercitation ullamco. '
                                    'In voluptate velit esse\ncillum '
                                    'dolore eu fugiat nulla.\n\nUt enim '
                                    'ad minim veniam.')

        node = section[1]
        assert node.get('orig_field_tag') == 'Yields'
        assert len(node) == 1
        assert len(node[0]) == 1
        assert node[0].astext() == '123'

    # Test: remove detected fields.
    def test_remove(self, assert_py_doc):
        assert_py_doc(
            text="""
            This is an ordinary paragraph.

            :Yields: Quis nostrud exercitation ullamco. In voluptate velit esse
                     cillum dolore eu fugiat nulla.
                     
                     Ut enim ad minim veniam.

            :Yields: 123
            :Yields:

            Ut enim ad minim veniam, quis nostrud.
            """,
            expected="""
            This is an ordinary paragraph.

            Ut enim ad minim veniam, quis nostrud.
            """
        )

    def test_report(self, parse_py_doc):
        env = parse_py_doc(
            add_report=True,
            text="""
            This is an ordinary paragraph.

            :Yields: 123
            :Yields:
            :Yields 23: sds

            Ut enim ad minim veniam, quis nostrud.
            """
        )
        doc = env['definition'].doc_block.document
        assert hasattr(doc, 'field_sections')

        report = env.get('reporter').report
        assert isinstance(report, list)
        assert len(report) == 2

        assert len(report[0]) == 8

        path, domain, line, col, ref_name, level, code, msg = report[0]
        assert path == '<string>'   # conftest setup this.
        assert domain == 'python'

        # NOTE: currently we drop position in the docstring
        # and use position of the ref (function, class).
        assert line == 0
        assert col == 0

        assert ref_name == 'test_func'
        assert level == logging.INFO
        assert code == Codes.MISSING
        assert msg == 'Content is missing [:Yields:]'

        path, domain, line, col, ref_name, level, code, msg = report[1]
        assert path == '<string>'   # conftest setup this.
        assert domain == 'python'

        # NOTE: currently we drop position in the docstring
        # and use position of the ref (function, class).
        assert line == 0
        assert col == 0

        assert ref_name == 'test_func'
        assert level == logging.INFO
        assert code == Codes.INCORRECT
        assert msg == 'Incorrect signature [:Yields:]'

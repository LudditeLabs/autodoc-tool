"""
This module implements fixtures and tools for testing with pytest.

In the tests you can access to the following features:

* ``pytest.g.*`` - namespace with helper functions and assertions::

      pytest.g.trim()
      pytest.g.assert_lines()
      pytest.g.parse_doc()
      pytest.g.assert_doc()

* Fixtures: ``parse_doc`` and ``assert_doc``. They are the same as
  ``pytest.g.parse_doc()`` and ``pytest.g.assert_doc()`` but allows to
  configure parameters based on module or class attributes.
  See the fixtures' docs for more info.
"""
import pytest
import logging
from unittest.mock import Mock
from functools import partial
from autodoc.utils import trim_docstring
from autodoc.utils import side_by_side
from autodoc.contentdb import Definition
from autodoc.context import Context
from autodoc.report import DomainReporter
from autodoc.settings import SettingsBuilder
from autodoc.python.domain import PythonDomain


class TestContext(Context):
    def __init__(self):
        log = logging.getLogger('testcontext')
        super(TestContext, self).__init__(log)

    def build_content_db(self, filename, paths, exclude, exclude_patterns,
                         builder):
        pass

    def get_content_db(self, filename):
        pass

    def analyze(self, content_db):
        pass


def assert_lines(actual, expected):
    """Assertion helper to compare lists of strings.

    Args:
        actual: Actual list.
        expected: Expected list.

    Raises:
        AssertionError if expected not equals actual. It also displays
        values side by side.

    See Also:
        :func:`side_by_side`.
    """
    __tracebackhide__ = True
    assert actual == expected, side_by_side(actual, expected,
                                            left_text='ACTUAL',
                                            right_text='EXPECTED',
                                            add_marker=True)


def create_definition(**kwargs):
    doc = (
        1,      # rowid
        None,   # id_member
        None,   # kind
        None,   # id_file
        1,      # start_line
        1,      # start_col
        None,   # end_line
        None,   # end_col
        None,   # docstring
        None,   # doc
    )

    definition = Definition(
        (),     # args
        1,      # id
        1,      # refid
        '',     # name
        1,      # definition
        1,      # type
        '',     # argsstring
        '',     # scope
        None,   # initializer
        None,   # bitfield
        None,   # read
        None,   # write
        0,      # visibility
        0,      # static
        0,      # const
        0,      # explicit
        0,      # inline
        0,      # final
        0,      # sealed
        0,      # new
        0,      # optional
        0,      # required
        0,      # volatile
        0,      # virtual
        0,      # mutable
        0,      # initonly
        0,      # attribute
        0,      # property
        0,      # readonly
        0,      # bound
        0,      # constrained
        0,      # transient
        0,      # maybevoid
        0,      # maybedefault
        0,      # maybeambiguous
        0,      # readable
        0,      # writable
        0,      # gettable
        0,      # privategettable
        0,      # protectedgettable
        0,      # settable
        0,      # privatesettable
        0,      # protectedsettable
        0,      # accessor
        0,      # addable
        0,      # removable
        0,      # raisable
        0,      # kind
        0,      # bodystart
        0,      # bodyend
        0,      # id_bodyfile
        1,      # id_file
        1,      # start_line
        1,      # start_col
        None,   # inherited_from
        None,   # compound_id
        None,   # compound_kind
        None,   # filename
        '',     # language
        *doc    # *other
    )

    for k, v in kwargs.items():
        if k.startswith('doc_block_'):
            setattr(definition.doc_block, k[10:], v)
        else:
            setattr(definition, k, v)

    return definition


class TestReporter(DomainReporter):
    def __init__(self, domain):
        super(TestReporter, self).__init__(domain)
        self.report = []

    def reset(self):
        self.report = []

    def add_report(self, code, message, line=0, col=0, level=None):
        name = self.definition.name if self.definition else None
        level = level or logging.INFO
        self.report.append((self._filename, self.domain.name, line, col,
                            name, level, code, message))


def parse_py_doc(text, settings=None, style='rst', defaultkw=None, trim=False,
                 **kw):
    """Parse python docstring and convert document tree back to text.

    This function is used to test how style converts document tree to
    text representation.

    Result docstring is stored in definition::

        env['definition'].doc_block.docstring

    Args:
        text: Docstring to parse.
        settings: Processing settings.
        style: Result docstring style.
        defaultkw: Default params.
        trim: Trim ``text``.
        **kw:

    Returns:
        Processing environment.
    """
    if trim:
        text = trim_docstring(text, as_string=True)

    if defaultkw:
        # Merge params.
        defaultkw.update(kw)
        kw = defaultkw.copy()

        # Override style.
        style = kw.pop('style', style)

        # Merge settings.
        s = kw.pop('settings', None)
        if s:
            if settings:
                s.update(settings)
            settings = s

    keep_transforms = kw.pop('keep_transforms', False)
    pass_lines = kw.pop('pass_lines', True)

    domain = PythonDomain()
    domain.reporter = TestReporter(domain)

    context = TestContext()
    context.register(domain)

    settings_builder = SettingsBuilder()
    settings_builder.collect(context)

    # --- Testing defaults
    settings = settings or {}
    # Easier to test - None means have blank line only for multi line docstring.
    settings.setdefault('first_blank_line', None)

    # Set to empty to have more space for line (bigger docstring width).
    settings.setdefault('docstring_quote', '')

    # With this width visual end of line in docstring will be the same as for
    # enclosing code.
    settings.setdefault('line_width', 68)

    settings_builder.add_from_dict({'py': {style: settings, 'style': style}})

    context.settings = settings_builder.get_settings()

    definition = create_definition(
        name='test_func',
        kind=1,
        start_line=1,
        start_col=1,
        bodystart=1,
        bodyend=3,
        args=kw.get('args', ()),
        filename='<string>',
        compound_id=kw.pop('compound_id', None),
        compound_kind=kw.pop('compound_kind', None),
        doc_block_docstring=text
    )



    db = Mock()

    env = domain.create_env(db, definition)
    with context.settings.with_settings(domain.settings_section):
        with context.settings.from_key('style'):

            # Make sure the style doesn't modify parsed document.
            # We don't need any extra modifications, because key point is to
            # test document-to-text translator.
            style = domain.get_style(domain.settings['style'])
            if not keep_transforms:
                style.transforms = []

            domain.reporter.env = env

            handler = domain.create_definition_handler(env)
            if not keep_transforms or 'transforms' in kw:
                handler.transforms = kw.pop('transforms', None)
            handler.setup()
            handler.build_document()

            if not pass_lines:
                env['source_lines'] = None
                env['num_source_lines'] = 0

            handler.apply_transforms()
            handler.translate_document_to_docstring()

    return env


def assert_py_doc(text, expected=None, **kwargs):
    """Compare input docstring with the one created by the given style.

    Args:
        text: Docstring to parse.
        expected: Expected docstring. ``docstring`` is used if not set.
        **kwargs: Parameters for the ``parse_py_doc``.

    Returns:
        Processing environment.
    """
    __tracebackhide__ = True

    text = trim_docstring(text)
    env = parse_py_doc('\n'.join(text), **kwargs)

    actual = env['definition'].doc_block.docstring.decode('utf-8').split('\n')
    expected = text if expected is None else trim_docstring(expected)

    assert_lines(actual, expected)
    return env


def pytest_namespace():
    """Define namespace with helper functions for tests.
    
    Tests can access to the namespace like this::
     
        import pytest
        ...
        
        pytest.g.parse_doc(...)
    """
    return {'g': {
        'trim': trim_docstring,
        'assert_lines': assert_lines,
        'parse_py_doc': parse_py_doc,
        'assert_py_doc': assert_py_doc,
    }}


# -- Fixtures -----------------------------------------------------------------

def add_if_defined(dest, src, attr, prefix=None):
    """Search attribute in the given source object and copy its value to
    ``dest``.

    Args:
        dest: Destination dict.
        src: Source object to search in.
        attr: Attribute to search in the ``src``.
        prefix: Attribute prefix. If set then result search name will be
            ``<prefix><attr>``.
    """
    full_key = (prefix + attr) if prefix else attr
    if hasattr(src, full_key):
        dest[attr] = getattr(src, full_key)


def search_params_in(src):
    """Helper function to get parameters from the given source.

    Args:
        src: Source object to search testing parameters.

    Returns:
        Dict with found parameters.
    """
    kwargs = {}
    prefix = 'docstring_'
    add_if_defined(kwargs, src, 'style', prefix)
    add_if_defined(kwargs, src, 'settings', prefix)
    add_if_defined(kwargs, src, 'transforms', prefix)
    add_if_defined(kwargs, src, 'keep_transforms', prefix)
    return kwargs


def search_params(request):
    """Helper function to get testing parameters from the context.

    Args:
        context: PyTest request context.

    Returns:
        Dict with found parameters.
    """
    params = search_params_in(request.module)
    cls_params = search_params_in(request.cls)
    params.update(cls_params)
    return params


@pytest.fixture(name='parse_py_doc')
def parse_py_doc_fixture(request):
    """This fixture returns :func:`parse_py_doc` with predefined parameters if
    they exists in the module or class.
    """
    params = search_params(request)
    return partial(parse_py_doc, defaultkw=params, trim=True)


@pytest.fixture(name='assert_py_doc')
def assert_py_doc_fixture(request):
    """This fixture returns :func:`assert_py_doc` with predefined parameters if
    they exists in the module or class.

    See Also:
        For more info check :func:`parse_doc_fixture`.
    """
    params = search_params(request)
    return partial(assert_py_doc, defaultkw=params)

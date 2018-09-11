# Test: references and targets.
class TestReference:
    # Test: reference nodes with disabled shorten option.
    def test_pep_rfc_refs_long(self, assert_py_doc):
        assert_py_doc(
            settings=dict(shorten_inline=False),
            text="""
            Test refs.
    
            :pep-reference:`287`, :PEP:`287`.
            
            :rfc-reference:`2822`, :RFC:`2822`.
            """
        )

    # Test: reference nodes with enabled shorten option.
    def test_pep_rfc_refs_short(self, assert_py_doc):
        assert_py_doc(
            settings=dict(shorten_inline=True),
            text="""
            Test refs.

            :pep-reference:`287`, :PEP:`287`.
            
            :rfc-reference:`2822`, :RFC:`2822`.
            """,
            expected="""
            Test refs.

            :PEP:`287`, :PEP:`287`.
            
            :RFC:`2822`, :RFC:`2822`.
            """
        )

    # Test: various references.
    def test_refs(self, assert_py_doc):
        assert_py_doc(
            settings=dict(line_width=60),
            text="""
            Comments begin with two dots and a space. Comments begin with `A
            Hyperlink`_ sdsadsa dsad two dots and a space 23032. Comments begin

            `__init__ <http:example.py.html#__init__>`__
            
            `*LINK* <Python home page_>`_
            
            `Simple1`_, Simple2_, Simple3__.
            
            :PEP:`287`, http://mailto.com
            mailto:some@bla.com

            The |bioha Zard| symbol must be used on containers used to
            dispose of medical |suB1|_ waste or |suB2|__.

            .. _Starts On-this-line: http://
              example.net/rst.html

            .. _Entirely below:
               http://example.
               sourceforge.net/123456.html

            .. _Python home page: http://www.python.org
            .. _link: `Python home page`_

            Oh yes, the _`Norwegian Blue`.  What's, um, what's wrong with it?

            .. _Python DOC-SIG mailing list archive:

            The hyperlink target above points to this paragraph.

            .. _hyperlink-name: link-block
            .. _Doc-SIG: http://mail.python.org/pipermail/doc-sig/

            `ITER <https://docs.python.org/2/library/functions.html#iter>`_ txt
            some other text.
            """,
            expected="""
            Comments begin with two dots and a space. Comments begin
            with `A Hyperlink`_ sdsadsa dsad two dots and a space 23032.
            Comments begin

            `__init__ <http:example.py.html#__init__>`__
            
            `*LINK* <Python home page_>`_

            `Simple1`_, Simple2_, Simple3__.
            
            :PEP:`287`, http://mailto.com mailto:some@bla.com

            The |bioha Zard| symbol must be used on containers used to
            dispose of medical |suB1|_ waste or |suB2|__.

            .. _Starts On-this-line: http://example.net/rst.html
            .. _Entirely below: http://example.sourceforge.net/123456.html
            .. _Python home page: http://www.python.org
            .. _link: `Python home page`_

            Oh yes, the _`Norwegian Blue`. What's, um, what's wrong with
            it?

            .. _Python DOC-SIG mailing list archive:

            The hyperlink target above points to this paragraph.

            .. _hyperlink-name: link-block
            .. _Doc-SIG: http://mail.python.org/pipermail/doc-sig/

            `ITER <https://docs.python.org/2/library/functions.html#iter>`_
            txt some other text.
            """
        )

# TODO: add more tests.
# Test: convert document to text when punctuation
# and enclosing chars exists near boxed words.
class TestPunctuation:
    def test_simple(self, assert_py_doc):
        assert_py_doc(
            settings=dict(line_width=80),
            text="""
            This is a paragraph.
    
            :myrole:`ddd`.
            
            Bla (:acronym:`ddd`). But ) :func:`xxx` with space!
            
            :any:`xxx` ... some word
            
            :any:`xxx`... some word
    
            ***dssd***, ```literal text```
            
            Line of text.
            """)

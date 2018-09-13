# Test: definition lists.
class TestDefinitionList:
    def test_def_list(self, assert_py_doc):
        assert_py_doc(
            text="""
            term 1
                Definition 1.

            term 2
                Definition 2, paragraph 1.

                Definition 2, paragraph 2.

            term 3 : classifier
                Definition 3.

            term 4 : classifier one : classifier two
                Definition 4.

                Bla *emphasis*, **strong emphasis**, ``literal text``,
                `interpreted text`.

                - One

                - Two
            """
        )
from __future__ import absolute_import
from autodoc.python.google.transforms.collect_fields import CollectGoogleSections

# These param will be loaded by the fixtures (assert_py_doc, parse_py_doc).
docstring_transforms = [CollectGoogleSections]


# TODO: improve me, these tests are very simple and stupid.
class TestCollectGooleSections:
    def test_notes(self, parse_py_doc):
        env = parse_py_doc(
            text="""
            Lorem ipsum dolor sit amet, consectetur adipiscing elit...

            Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
            Ut enim ad minim veniam.

            .. admonition:: Notes

               Quis nostrud exercitation ullamco. In voluptate velit esse
               cillum dolore eu fugiat nulla.

               Ut enim ad minim veniam.

            .. admonition:: Notes

               Lorem ipsum dolor sit amet, consectetur adipiscing elit.
            """
        )

        doc = env['definition'].doc_block.document
        assert hasattr(doc, 'field_sections')

        section = doc.field_sections.get('notes')
        assert section is not None

        # Notes section contains paragraph of the found admonitions.
        # See Also: CollectGoogleSections.process_notes()
        assert len(section) == 3

    def test_note(self, parse_py_doc):
        env = parse_py_doc(
            text="""
            Lorem ipsum dolor sit amet, consectetur adipiscing elit...

            Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
            Ut enim ad minim veniam.

            .. note:: 

               Quis nostrud exercitation ullamco. In voluptate velit esse
               cillum dolore eu fugiat nulla.

               Ut enim ad minim veniam.

            .. note:: Lorem ipsum dolor sit amet, consectetur adipiscing elit.
            """
        )

        doc = env['definition'].doc_block.document
        assert hasattr(doc, 'field_sections')

        section = doc.field_sections.get('note')
        assert section is not None
        assert len(section) == 2

    def test_examples(self, parse_py_doc):
        env = parse_py_doc(
            text="""
            Lorem ipsum dolor sit amet, consectetur adipiscing elit...

            Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
            Ut enim ad minim veniam.

            .. admonition:: Examples

               Examples should be written in doctest format, and should
               illustrate how to use the function.
        
               >>> print([i for i in example_generator(4)])
               [0, 1, 2, 3]

            .. admonition:: Examples

               Examples 2

               >>> print([i for i in example_generator(4)])
               [0, 1, 2, 3]
            """
        )

        doc = env['definition'].doc_block.document
        assert hasattr(doc, 'field_sections')

        section = doc.field_sections.get('examples')
        assert section is not None

        # 'Examples' section contains paragraph of the found admonitions.
        # See Also: CollectGoogleSections.process_examples()
        assert len(section) == 4

    def test_example(self, parse_py_doc):
        env = parse_py_doc(
            text="""
            Lorem ipsum dolor sit amet, consectetur adipiscing elit...

            Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
            Ut enim ad minim veniam.

            .. admonition:: Example

               Examples should be written in doctest format, and should
               illustrate how to use the function.
        
               >>> print([i for i in example_generator(4)])
               [0, 1, 2, 3]

            .. admonition:: Example

               Examples 2

               >>> print([i for i in example_generator(4)])
               [0, 1, 2, 3]
            """
        )

        doc = env['definition'].doc_block.document
        assert hasattr(doc, 'field_sections')

        section = doc.field_sections.get('example')
        assert section is not None

        # 'Example' section contains paragraph of the found admonitions.
        # See Also: CollectGoogleSections.process_example()
        assert len(section) == 4

    def test_references(self, parse_py_doc):
        env = parse_py_doc(
            text="""
            Lorem ipsum dolor sit amet, consectetur adipiscing elit...

            Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
            Ut enim ad minim veniam.

            .. admonition:: References

               Same as examples section.
                
            .. admonition:: References

               Quis autem vel eum iure reprehenderit qui in ea voluptate
               Examples should be written in doctest format, and should
               illustrate how to use the function.
            """
        )

        doc = env['definition'].doc_block.document
        assert hasattr(doc, 'field_sections')

        section = doc.field_sections.get('references')
        assert section is not None
        assert len(section) == 2

    def test_seealso(self, parse_py_doc):
        env = parse_py_doc(
            text="""
            Lorem ipsum dolor sit amet, consectetur adipiscing elit...

            Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
            Ut enim ad minim veniam.

            .. seealso::

               Same as examples section.
                
               Quis autem vel eum iure reprehenderit qui in ea voluptate
               Examples should be written in doctest format, and should
               illustrate how to use the function.
            
            .. seealso:: Short text.
            """
        )

        doc = env['definition'].doc_block.document
        assert hasattr(doc, 'field_sections')

        section = doc.field_sections.get('seealso')
        assert section is not None
        assert len(section) == 2

    def test_todo(self, parse_py_doc):
        env = parse_py_doc(
            text="""
        Lorem ipsum dolor sit amet, consectetur adipiscing elit...

        Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
        Ut enim ad minim veniam.

        .. todo::

           * For module TODOs
           * You have to also use ``sphinx.ext.todo`` extension
        
        .. todo:: Do something smart.
        """
        )

        doc = env['definition'].doc_block.document
        assert hasattr(doc, 'field_sections')

        section = doc.field_sections.get('todo')
        assert section is not None
        assert len(section) == 2

    def test_warning(self, parse_py_doc):
        env = parse_py_doc(
            text="""
        Lorem ipsum dolor sit amet, consectetur adipiscing elit...

        Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
        Ut enim ad minim veniam.

        .. warning::
        
           Quis autem vel eum iure reprehenderit
           Examples should be written in doctest.
            
        .. warning:: suscipit laboriosam, nisi ut aliquid ex ea commodi consequatur?
        """
        )

        doc = env['definition'].doc_block.document
        assert hasattr(doc, 'field_sections')

        section = doc.field_sections.get('warning')
        assert section is not None
        assert len(section) == 2

    def test_warn(self, parse_py_doc):
        env = parse_py_doc(
            text="""
        Lorem ipsum dolor sit amet, consectetur adipiscing elit...

        :Warns: * **Some text.**
                * **Quis autem vel eum iure reprehenderit**
                * **Examples should be written in doctest.**

        Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
        Ut enim ad minim veniam.

        :Warns: * **Some text.**
                * **Quis autem vel eum iure reprehenderit**
                * **Examples should be written in doctest.**
        """
        )

        doc = env['definition'].doc_block.document
        assert hasattr(doc, 'field_sections')

        section = doc.field_sections.get('warns')
        assert section is not None
        assert len(section) == 2

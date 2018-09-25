from autodoc.contentdb import Arg

docstring_style = 'google'
docstring_keep_transforms = True


# Test: how translation from document to Google style works. Args section.
class TestAgs:
    # Test: simple situation - function with 2 params with description.
    def test_simple(self, assert_py_doc):
        assert_py_doc(
            args=(Arg('sender', []), Arg('priority', [])),
            text="""
            Lorem ipsum dolor sit amet, consectetur adipiscing elit...
            
            Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
            Ut enim ad minim veniam.
            
            Args:
                sender: Quis nostrud exercitation ullamco.
                priority: In voluptate velit esse cillum dolore
                    eu fugiat nulla.
            """,
            expected="""
            Lorem ipsum dolor sit amet, consectetur adipiscing elit...

            Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
            Ut enim ad minim veniam.

            Args:
                sender: Quis nostrud exercitation ullamco.
                priority: In voluptate velit esse cillum dolore eu fugiat nulla.
            """)

    # Test: empty args.
    def test_empty(self, assert_py_doc):
        # Here we have function without args but docstring contains few args.
        # They will be removed by the SyncParametersWithSpec; Args section
        # will be removed too because of empty content.
        assert_py_doc(
            text="""
            Lorem ipsum dolor sit amet, consectetur adipiscing elit...
            
            Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
            Ut enim ad minim veniam.
            
            Args:
                sender: Quis nostrud exercitation ullamco.
                priority: In voluptate velit esse cillum dolore eu fugiat nulla.
            """,
            expected="""
            Lorem ipsum dolor sit amet, consectetur adipiscing elit...

            Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
            Ut enim ad minim veniam.
            """)

    # Test: arguments with types defined.
    def test_with_types(self, assert_py_doc):
        args = (Arg('sender', ['str']),
                Arg('recipient', ['str']),
                Arg('message_body', ['str']),
                Arg('priority', ['integer', 'float']))

        # Here 'message_body' has different type - will be updates.
        # Other params will have types.
        # Also 'priority' will be added.
        assert_py_doc(
            args=args,
            text="""
            Lorem ipsum dolor sit amet, consectetur adipiscing elit...
            
            Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
            Ut enim ad minim veniam.
            
            Args:
                sender: Quis nostrud exercitation ullamco.
                recipient: Laboris nisi ut aliquip ex ea commodo.
                message_body (int): Duis aute irure dolor in reprehenderit.
            """,
            expected="""
            Lorem ipsum dolor sit amet, consectetur adipiscing elit...

            Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
            Ut enim ad minim veniam.

            Args:
                sender (str): Quis nostrud exercitation ullamco.
                recipient (str): Laboris nisi ut aliquip ex ea commodo.
                message_body (str): Duis aute irure dolor in reprehenderit.
                priority (integer, float):
            """)

    # Test: function has no types, but docstring has.
    # In this situation we have to preserve defined in the docstring type.
    def test_no_types(self, assert_py_doc):
        assert_py_doc(
            args=(Arg('sender', []), Arg('priority', [])),
            text="""
            Lorem ipsum dolor sit amet, consectetur adipiscing elit...
            
            Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
            Ut enim ad minim veniam.
            
            Args:
                sender: Quis nostrud exercitation ullamco.
                priority (int): Duis aute irure dolor in reprehenderit.
            """,
            expected="""
            Lorem ipsum dolor sit amet, consectetur adipiscing elit...

            Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
            Ut enim ad minim veniam.

            Args:
                sender: Quis nostrud exercitation ullamco.
                priority (int): Duis aute irure dolor in reprehenderit.
            """)

    # Test: parse plain reStructuredText.
    def test_from_rst(self, assert_py_doc):
        assert_py_doc(
            args=(Arg('sender', []), Arg('priority', [])),
            text="""
            Lorem ipsum dolor sit amet, consectetur adipiscing elit...
            
            Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
            Ut enim ad minim veniam.
            
            :param sender: Quis nostrud exercitation ullamco.
            :param priority: Duis aute irure dolor in reprehenderit.
            :type priority: int
            """,
            expected="""
            Lorem ipsum dolor sit amet, consectetur adipiscing elit...

            Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
            Ut enim ad minim veniam.

            Args:
                sender: Quis nostrud exercitation ullamco.
                priority (int): Duis aute irure dolor in reprehenderit.
            """)

    # Test: check if blocks indentation works correctly.
    # There must be 4 spaces indent for nested paragraphs.
    def test_indent(self, assert_py_doc):
        assert_py_doc(
            args=(Arg('sender', []), Arg('priority', [])),
            text="""
            Lorem ipsum dolor sit amet, consectetur adipiscing elit...
            
            Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
            Ut enim ad minim veniam.
            
            Args:
                sender: Quis nostrud exercitation ullamco.
                            Excepteur sint occaecat cupidatat non proident,
                priority (int): Duis aute irure dolor in reprehenderit::
                
                    Excepteur sint occaecat cupidatat non proident,
            """,
            expected="""
            Lorem ipsum dolor sit amet, consectetur adipiscing elit...

            Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
            Ut enim ad minim veniam.

            Args:
                sender: Quis nostrud exercitation ullamco. Excepteur sint
                    occaecat cupidatat non proident,
                priority (int): Duis aute irure dolor in reprehenderit::
                
                        Excepteur sint occaecat cupidatat non proident,
            """)

    # Test: check if wrapping works correctly.
    def test_wrap(self, assert_py_doc):
        assert_py_doc(
            settings=dict(line_width=60),
            args=(Arg('sender', []), Arg('priority', [])),
            text="""
            Lorem ipsum dolor sit amet, consectetur adipiscing elit...
            
            Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
            Ut enim ad minim veniam.
            
            Args:
                sender: Quis nostrud exercitation ullamco.
                    Excepteur sint occaecat cupidatat non proident,
                priority (int): Duis aute irure dolor in reprehenderit
                    Excepteur sint occaecat cupidatat non proident,
            """,
            expected="""
            Lorem ipsum dolor sit amet, consectetur adipiscing elit...

            Sed do eiusmod tempor incididunt ut labore et dolore magna
            aliqua. Ut enim ad minim veniam.

            Args:
                sender: Quis nostrud exercitation ullamco. Excepteur
                    sint occaecat cupidatat non proident,
                priority (int): Duis aute irure dolor in reprehenderit
                    Excepteur sint occaecat cupidatat non proident,
            """)


# Test: how translation from document to Google style works. Returns section.
class TestReturns:
    def test_simple(self, assert_py_doc):
        assert_py_doc(
            text="""
            Lorem ipsum dolor sit amet, consectetur adipiscing elit...

            Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
            Ut enim ad minim veniam.

            Returns:
                Quis nostrud exercitation ullamco. In voluptate velit esse
                cillum dolore eu fugiat nulla.
            """,
            expected="""
            Lorem ipsum dolor sit amet, consectetur adipiscing elit...

            Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
            Ut enim ad minim veniam.

            Returns:
                Quis nostrud exercitation ullamco. In voluptate velit esse
                cillum dolore eu fugiat nulla.
            """)

    # Test: returns section with type specified.
    def test_with_type(self, assert_py_doc):
        assert_py_doc(
            text="""
            Lorem ipsum dolor sit amet, consectetur adipiscing elit...

            Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
            Ut enim ad minim veniam.
            
            Returns:
                bool: True if successful, False otherwise.
        
                The return type is optional and may be specified at the beginning of
                the ``Returns`` section followed by a colon.
        
                The ``Returns`` section may span multiple lines and paragraphs.
                Following lines should be indented to match the first line.
        
                The ``Returns`` section supports any reStructuredText formatting,
                including literal blocks::
        
                    {
                        'param1': param1,
                        'param2': param2
                    }
            """,
            expected="""
            Lorem ipsum dolor sit amet, consectetur adipiscing elit...

            Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
            Ut enim ad minim veniam.

            Returns:
                bool: True if successful, False otherwise.
        
                The return type is optional and may be specified at the
                beginning of the ``Returns`` section followed by a colon.
        
                The ``Returns`` section may span multiple lines and paragraphs.
                Following lines should be indented to match the first line.
        
                The ``Returns`` section supports any reStructuredText
                formatting, including literal blocks::
        
                    {
                        'param1': param1,
                        'param2': param2
                    }
            """)

    # Test: returns section with multiple types.
    def test_with_multi_types(self, assert_py_doc):
        assert_py_doc(
            text="""
            Lorem ipsum dolor sit amet, consectetur adipiscing elit...

            Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
            Ut enim ad minim veniam.

            :returns:
            :rtype: something
            
            :returns: Bla bla

            :returns: One more bla bla.
            :rtype: string

            Returns:
                bool: True if successful, False otherwise.
        
                The return type is optional and may be specified at the
                beginning of the ``Returns`` section followed by a colon.
            """,
            expected="""
            Lorem ipsum dolor sit amet, consectetur adipiscing elit...

            Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
            Ut enim ad minim veniam.

            Returns:
                something:
                
                Bla bla

                string: One more bla bla.
                
                bool: True if successful, False otherwise.
        
                The return type is optional and may be specified at the
                beginning of the ``Returns`` section followed by a colon.
            """)

        # Note: result Returns section will be converted to different structure
        # by the napoleon parser. Check this.
        # 'something' type will be merge with next paragraph.
        # TODO: improve somehow; put descriptions without a type to the end?

        assert_py_doc(
            text="""
            Lorem ipsum dolor sit amet, consectetur adipiscing elit...

            Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
            Ut enim ad minim veniam.

            Returns:
                something:
                
                Bla bla

                string: One more bla bla.
                
                bool: True if successful, False otherwise.
        
                The return type is optional and may be specified at the
                beginning of the ``Returns`` section followed by a colon.
            """,
            expected="""
            Lorem ipsum dolor sit amet, consectetur adipiscing elit...

            Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
            Ut enim ad minim veniam.

            Returns:
                something: Bla bla

                string: One more bla bla.
                
                bool: True if successful, False otherwise.
        
                The return type is optional and may be specified at the
                beginning of the ``Returns`` section followed by a colon.
            """)


# Test: how translation from document to Google style works. Raises section.
class TestRaises:
    # Test: simple case.
    def test_simple(self, assert_py_doc):
        assert_py_doc(
            text="""
            Lorem ipsum dolor sit amet, consectetur adipiscing elit...

            Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
            Ut enim ad minim veniam.

            :raises: dff
           
            Raises:
                dff asdas
                ValueError: If `param2` is equal to `param1`.

            :raises KeyError: Sed do eiusmod tempor incididunt ut labore
                              et dolore magna aliqua. Ut enim ad minim veniam.
            """,
            expected="""
            Lorem ipsum dolor sit amet, consectetur adipiscing elit...

            Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
            Ut enim ad minim veniam.

            Raises:
                * dff
                
                * dff asdas
                
                * ValueError: If `param2` is equal to `param1`.
                
                * KeyError: Sed do eiusmod tempor incididunt ut labore et dolore
                  magna aliqua. Ut enim ad minim veniam.
            """)

    # Test: reparse google-styled raises section.
    def test_reparse(self, assert_py_doc):
        assert_py_doc(
            text="""
            Lorem ipsum dolor sit amet, consectetur adipiscing elit...

            Sed do eiusmod tempor incididunt ut labore et dolore magna.
            Ut enim ad minim veniam.

            Raises:
                * dff
                
                * dff asdas
                
                * ValueError: If `param2` is equal to `param1`.
                
                * KeyError: Sed do eiusmod tempor incididunt ut labore
                  et dolore magna aliqua. Ut enim ad minim veniam.
            """,
            expected="""
            Lorem ipsum dolor sit amet, consectetur adipiscing elit...

            Sed do eiusmod tempor incididunt ut labore et dolore magna. Ut enim
            ad minim veniam.

            Raises:
                * dff
                
                * dff asdas
                
                * ValueError: If `param2` is equal to `param1`.
                
                * KeyError: Sed do eiusmod tempor incididunt ut labore et dolore
                  magna aliqua. Ut enim ad minim veniam.
            """)

    # Test: incorrect structure - missing type.
    # In this case list will be constructed.
    def test_incorrect(self, assert_py_doc):
        assert_py_doc(
            text="""
            Lorem ipsum dolor sit amet, consectetur adipiscing elit...

            Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
            Ut enim ad minim veniam.

            Raises:
                Quis nostrud exercitation ullamco. In voluptate velit esse
                cillum dolore eu fugiat nulla.
            """,
            expected="""
            Lorem ipsum dolor sit amet, consectetur adipiscing elit...

            Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
            Ut enim ad minim veniam.

            Raises:
                * Quis nostrud exercitation ullamco. In voluptate velit esse

                * cillum dolore eu fugiat nulla.
            """)


class TestYields:
    def test_simple(self, assert_py_doc):
        assert_py_doc(
            text="""
            Lorem ipsum dolor sit amet, consectetur adipiscing elit...

            Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
            Ut enim ad minim veniam.

            Yields:
                The next number in the range of 0 to `n` - 1.
                uis nostrud exercitation ullamco. In voluptate
                
                velit esse.
            """,
            expected="""
            Lorem ipsum dolor sit amet, consectetur adipiscing elit...

            Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
            Ut enim ad minim veniam.

            Yields:
                The next number in the range of 0 to `n` - 1. uis nostrud
                exercitation ullamco. In voluptate
                
                velit esse.
            """)

    def test_multiple(self, assert_py_doc):
        assert_py_doc(
            text="""
            Lorem ipsum dolor sit amet, consectetur adipiscing elit...

            Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
            Ut enim ad minim veniam.

            :Yields: In voluptate.

            Yields:
                The next number in the range of 0 to `n` - 1.
                uis nostrud exercitation ullamco. In voluptate
                
                velit esse.
                
            Yields:
                int: Some value.
            
            """,
            expected="""
            Lorem ipsum dolor sit amet, consectetur adipiscing elit...

            Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
            Ut enim ad minim veniam.

            Yields:
                In voluptate.

                The next number in the range of 0 to `n` - 1. uis nostrud
                exercitation ullamco. In voluptate
                
                velit esse.
                
                *int* -- Some value.
            """)


# * Note/Notes
# * Examples
# * References
class TestAdmonitions:
    def test_note(self, assert_py_doc):
        assert_py_doc(
            text="""
            Lorem ipsum dolor sit amet, consectetur adipiscing elit...

            Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
            Ut enim ad minim veniam.

            .. note:: Nemo enim ipsam voluptatem quia voluptas.

            Note:
                The next number in the range of 0 to `n` - 1.
                uis nostrud exercitation ullamco. In voluptate
                
                velit esse.
                
            Notes:
                Ut enim ad minima veniam, quis nostrum exercitationem
                ullam corporis.
                
                suscipit laboriosam, nisi ut aliquid ex ea commodi consequatur?
            """,
            expected="""
            Lorem ipsum dolor sit amet, consectetur adipiscing elit...

            Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
            Ut enim ad minim veniam.

            Note:
                Nemo enim ipsam voluptatem quia voluptas.

                The next number in the range of 0 to `n` - 1. uis nostrud
                exercitation ullamco. In voluptate
                
                velit esse.
                
            Notes:
                Ut enim ad minima veniam, quis nostrum exercitationem ullam
                corporis.
                
                suscipit laboriosam, nisi ut aliquid ex ea commodi consequatur?
            """)
    def test_note_complex(self, assert_py_doc):
        assert_py_doc(
            text="""Run merge and simulation for each file-list in :attr:`_filenames`.

            Merge is performed by :class:`MergedPortfolioSimulator` in parallel
            mode.

            Notes:
                How parallel processing happens:
    
                Worker creates simulator instances and pickles them in a temp files.
                Then it returns pickled filenames to main process where simulators
                gets restored from the files::
    
                    create -> pickle -> save to file -> filenames
                        -> main process -> restore
    
                Another way is just pass instances via multiprocessing queue::
    
                    create -> pickle -> queue -> main process -> restore
    
                but it could consume a lot of memory while transferring data if
                instances are heavy. So we use temp files instead of queue.
            """,
            expected="""
            Run merge and simulation for each file-list in :attr:`_filenames`.

            Merge is performed by :class:`MergedPortfolioSimulator` in parallel
            mode.

            Notes:
                How parallel processing happens:
    
                Worker creates simulator instances and pickles them in a temp files.
                Then it returns pickled filenames to main process where simulators
                gets restored from the files::
    
                    create -> pickle -> save to file -> filenames
                        -> main process -> restore
    
                Another way is just pass instances via multiprocessing queue::
    
                    create -> pickle -> queue -> main process -> restore
    
                but it could consume a lot of memory while transferring data if
                instances are heavy. So we use temp files instead of queue.
            """, settings=dict(line_width=72))

    def test_examples(self, assert_py_doc):
        assert_py_doc(
            # Pass source lines to have correct indentation
            # for the literal block:
            #
            #     $ dsodksds sds
            #
            # It will be un indented otherwise because first character '$' is a
            # quotation marker.
            # See also: LiteralBlockMixin.visit_literal_block()
            pass_lines=True,
            text="""
            Lorem ipsum dolor sit amet, consectetur adipiscing elit...

            Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
            Ut enim ad minim veniam.

            .. admonition:: Example
            
               Nemo enim ipsam voluptatem quia voluptas.

            Examples:
                Examples should be written in doctest format, and should
                illustrate how to use the function.
        
                >>> print([i for i in example_generator(4)])
                [0, 1, 2, 3]

            Example:
                Examples should be written in doctest format.
                Untrue, you can use any formatting::
                
                    $ dsodksds sds
            """,
            expected="""
            Lorem ipsum dolor sit amet, consectetur adipiscing elit...

            Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
            Ut enim ad minim veniam.

            Example:
                Nemo enim ipsam voluptatem quia voluptas.

                Examples should be written in doctest format. Untrue, you can
                use any formatting::
                
                    $ dsodksds sds

            Examples:
                Examples should be written in doctest format, and should
                illustrate how to use the function.
        
                >>> print([i for i in example_generator(4)])
                [0, 1, 2, 3]
            """)

    def test_references(self, assert_py_doc):
        assert_py_doc(
            text="""
            Lorem ipsum dolor sit amet, consectetur adipiscing elit...

            Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
            Ut enim ad minim veniam.

            .. admonition:: References

               Same as examples section.

            References:
                Quis autem vel eum iure reprehenderit qui in ea voluptate
                Examples should be written in doctest format, and should
                illustrate how to use the function.
            """,
            expected="""
            Lorem ipsum dolor sit amet, consectetur adipiscing elit...

            Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
            Ut enim ad minim veniam.

            References:
                Same as examples section.
                
                Quis autem vel eum iure reprehenderit qui in ea voluptate
                Examples should be written in doctest format, and should
                illustrate how to use the function.
            """)


class TestSeeAlso:
    def test(self, assert_py_doc):
        assert_py_doc(
            text="""
            Lorem ipsum dolor sit amet, consectetur adipiscing elit...

            Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
            Ut enim ad minim veniam.

            .. seealso:: Nemo enim ipsam voluptatem quia voluptas.

            See Also:
                The next number in the range of 0 to `n` - 1.
                uis nostrud exercitation ullamco. In voluptate
                
                velit esse.
            """,
            expected="""
            Lorem ipsum dolor sit amet, consectetur adipiscing elit...

            Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
            Ut enim ad minim veniam.

            See Also:
                Nemo enim ipsam voluptatem quia voluptas.

                The next number in the range of 0 to `n` - 1. uis nostrud
                exercitation ullamco. In voluptate
                
                velit esse.
            """)


class TestTodo:
    def test(self, assert_py_doc):
        assert_py_doc(
            text="""
            Lorem ipsum dolor sit amet, consectetur adipiscing elit...

            Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
            Ut enim ad minim veniam.

            .. todo:: Do something smart.

            Todo:
                * For module TODOs
                * You have to also use ``sphinx.ext.todo`` extension
                
                * todo 3
            """,
            expected="""
            Lorem ipsum dolor sit amet, consectetur adipiscing elit...

            Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
            Ut enim ad minim veniam.

            Todo:
                Do something smart.

            Todo:
                * For module TODOs
                * You have to also use ``sphinx.ext.todo`` extension
                
                * todo 3
            """)


class TestWarnings:
    # For single directive title must be 'Warning'
    def test(self, assert_py_doc):
        assert_py_doc(
            text="""
            Lorem ipsum dolor sit amet, consectetur adipiscing elit...

            Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
            Ut enim ad minim veniam.

            .. warning::

               Quis autem vel eum iure reprehenderit qui in ea voluptate
               Examples should be written in doctest.
            """,
            expected="""
            Lorem ipsum dolor sit amet, consectetur adipiscing elit...

            Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
            Ut enim ad minim veniam.

            Warning:
                Quis autem vel eum iure reprehenderit qui in ea voluptate
                Examples should be written in doctest.
            """)

    # For multiple directives title must be 'Warnings'
    def test_multi(self, assert_py_doc):
        assert_py_doc(
            text="""
            Lorem ipsum dolor sit amet, consectetur adipiscing elit...

            Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
            Ut enim ad minim veniam.

            .. warning::

               Quis autem vel eum iure reprehenderit qui in ea voluptate

            Warning:
                Quis autem vel eum iure reprehenderit
                Examples should be written in doctest.
                
            Warnings:
                suscipit laboriosam, nisi ut aliquid ex ea commodi consequatur?
            """,
            expected="""
            Lorem ipsum dolor sit amet, consectetur adipiscing elit...

            Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
            Ut enim ad minim veniam.

            Warnings:
                Quis autem vel eum iure reprehenderit qui in ea voluptate

                Quis autem vel eum iure reprehenderit Examples should be written
                in doctest.

                suscipit laboriosam, nisi ut aliquid ex ea commodi consequatur?
            """)

    def test_warn(self, assert_py_doc):
        # NOTE: here xxxxx precedes other content because it's unexpected
        # node: we expect bullet lists.
        # See style_google.AddSections.process_warns()
        assert_py_doc(
            text="""
            Lorem ipsum dolor sit amet, consectetur adipiscing elit...
    
            :Warns: * **Some text.**
                    * **Quis autem vel eum iure reprehenderit**
                    * **Examples should be written in doctest.**
    
            Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
            Ut enim ad minim veniam.
    
            :Warns: * **Some text.**
                    * **Quis autem vel eum *iure* reprehenderit**
                    * **Examples should be written in doctest.**

            :Warns: xxxxx
            :Warns:
            """,
            expected="""
            Lorem ipsum dolor sit amet, consectetur adipiscing elit...
   
            Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
            Ut enim ad minim veniam.
    
            Warns:
                xxxxx

                Some text. Quis autem vel eum iure reprehenderit Examples should
                be written in doctest. Some text. Quis autem vel eum *iure*
                reprehenderit Examples should be written in doctest.
            """)

import os
import os.path as op
import sys
import sqlite3
import subprocess
import tempfile
import json
from collections import namedtuple


class ContentDbError(Exception):
    pass


# TODO: add feature to update existing DB.
class ContentDbBuilder:
    """Content DB builder.

    It creates a database from input paths.
    """
    def __init__(self, context, exe=None):
        """Construct content DB builder.

        Args:
            context: Application context :class:`Context`.
            exe: External executable to build content DB.
        """
        self.context = context
        self._exe = exe or self._get_exe()

    @property
    def logger(self):
        """Logger."""
        return self.context.logger

    def _get_exe(self):
        """Build filename to execute."""
        cmd = os.environ.get('AUTODOC_CONTENT_BUILDER')

        # By default call '<app_dir>/contentdb' where <app_dir> is a directory
        # with the autodoc executable.
        if not cmd:
            cmd = op.abspath(op.dirname(sys.argv[0]))
            cmd = op.join(cmd, 'contentdb')

            # Append '.exe' extension for Windows platforms.
            try:
                sys.winver
            except AttributeError:
                pass
            else:
                cmd += '.exe'

        return cmd

    def _get_env(self):
        """Get environment vars for the external builder exe.

        Returns:
            Dict with environment variables or ``None``.

        Notes:
            If ``CONTENT_BUILDER_NOENV`` environment variable is set then
            returns ``None``.
        """
        # These vars used by contentdb tool to correctly load python modules.
        if 'CONTENT_BUILDER_NOENV' not in os.environ:
            this_dir = op.abspath(op.dirname(sys.argv[0]))
            lib_dir = op.join(this_dir, 'lib')
            lib_zip = op.join(lib_dir, 'library.zip')
            return {
                'PYTHONHOME': this_dir,
                'PYTHONPATH': lib_dir + os.pathsep + lib_zip
            }

    def build(self, output, paths, exclude=None, exclude_patterns=None,
              file_patterns=None):
        """Build content database.

        Args:
            output: Output content DB filename.
            paths: List of paths to process.
            exclude: List of paths or filenames to exclude.
            exclude_patterns: Wildcard patterns to exclude.
            file_patterns: Files wildcard patterns.

        Returns:
            :class:`ContentDb` instance.
        """
        if not op.exists(self._exe):
            raise ContentDbError('Content DB builder is not found: %s'
                                 % self._exe)

        temp_dir = tempfile.mkdtemp()

        cmd = [self._exe, '-T', temp_dir, '-o', output]

        if exclude:
            for path in exclude:
                cmd.extend(('-e', path))

        if exclude_patterns:
            for path in exclude_patterns:
                cmd.extend(('-x', path))

        if file_patterns:
            cmd.extend(('-p', ';'.join(file_patterns)))

        cmd += paths

        try:
            subprocess.run(cmd, check=True, env=self._get_env())
        except subprocess.CalledProcessError:
            raise ContentDbError

        if not op.exists(output):
            raise ContentDbError('Error creating content DB %s' % output)

        return ContentDb(self.context, output)


class DocBlock:
    __slots__ = ['id', 'id_member', 'kind', 'id_file', 'start_line',
                 'start_col', 'end_line', 'end_col', 'docstring', 'document']

    def __init__(self, rowid, id_member, kind, id_file, start_line, start_col,
                 end_line, end_col, docstring, doc):
        self.id = rowid
        self.id_member = id_member
        self.kind = kind                # 0:member 1:compound
        self.id_file = id_file
        self.start_line = start_line
        self.start_col = start_col
        self.end_line = end_line
        self.end_col = end_col
        if docstring is not None and isinstance(docstring, bytes):
            self.docstring = docstring.decode('utf-8')
        else:
            self.docstring = docstring
        self.document = doc


Arg = namedtuple('Arg', ['name', 'type_list'])
_empty_args = ()


class Definition:
    __slots__ = ['id', 'refid', 'name', 'definition', 'type', 'argsstring',
                 'scope', 'initializer', 'bitfield', 'read', 'write',
                 'visibility', 'is_static', 'is_const', 'is_explicit',
                 'is_inline', 'is_final', 'is_sealed', 'is_new', 'is_optional',
                 'is_required', 'is_volatile', 'virtual', 'is_mutable',
                 'is_initonly', 'is_attribute', 'is_property', 'is_readonly',
                 'is_bound', 'is_constrained', 'is_transient', 'is_maybevoid',
                 'is_maybedefault', 'is_maybeambiguous', 'is_readable',
                 'is_writable', 'is_gettable', 'is_privategettable',
                 'is_protectedgettable', 'is_settable', 'is_privatesettable',
                 'is_protectedsettable', 'accessor', 'is_addable',
                 'is_removable', 'is_raisable', 'kind', 'bodystart', 'bodyend',
                 'id_bodyfile', 'id_file', 'start_line', 'start_col',
                 'inherited_from', 'compound_id', 'compound_kind', 'filename',
                 'language', 'args', 'doc_block'
                 ]

    def __init__(self, args, id, refid, name, definition, type, argsstring,
                 scope, initializer, bitfield, read, write, visibility, static,
                 const, explicit, inline, final, sealed, new, optional,
                 required, volatile, virtual, mutable, initonly, attribute,
                 property, readonly, bound, constrained, transient, maybevoid,
                 maybedefault, maybeambiguous, readable, writable, gettable,
                 privategettable, protectedgettable, settable, privatesettable,
                 protectedsettable, accessor, addable, removable, raisable,
                 kind, bodystart, bodyend, id_bodyfile, id_file, start_line,
                 start_col, inherited_from, compound_id, compound_kind,
                 filename, language, *other):
        self.id                     = id
        self.refid                  = refid
        self.name                   = name
        self.definition             = definition
        self.type                   = type
        self.argsstring             = argsstring
        self.scope                  = scope
        self.initializer            = initializer
        self.bitfield               = bitfield
        self.read                   = read
        self.write                  = write
        self.visibility             = visibility        # 0:public 1:protected
                                                        # 2:private 3:package
        self.is_static              = bool(static)
        self.is_const               = bool(const)
        self.is_explicit            = bool(explicit)
        self.is_inline              = bool(inline)
        self.is_final               = bool(final)
        self.is_sealed              = bool(sealed)
        self.is_new                 = bool(new)
        self.is_optional            = bool(optional)
        self.is_required            = bool(required)
        self.is_volatile            = bool(volatile)
        self.virtual                = virtual           # 0:no 1:virtual
                                                        # 2:pure-virtual
        self.is_mutable             = bool(mutable)
        self.is_initonly            = bool(initonly)
        self.is_attribute           = bool(attribute)
        self.is_property            = bool(property)
        self.is_readonly            = bool(readonly)
        self.is_bound               = bool(bound)
        self.is_constrained         = bool(constrained)
        self.is_transient           = bool(transient)
        self.is_maybevoid           = bool(maybevoid)
        self.is_maybedefault        = bool(maybedefault)
        self.is_maybeambiguous      = bool(maybeambiguous)
        self.is_readable            = bool(readable)
        self.is_writable            = bool(writable)
        self.is_gettable            = bool(gettable)
        self.is_privategettable     = bool(privategettable)
        self.is_protectedgettable   = bool(protectedgettable)
        self.is_settable            = bool(settable)
        self.is_privatesettable     = bool(privatesettable)
        self.is_protectedsettable   = bool(protectedsettable)
        self.accessor               = accessor          # 1:assign 2:copy
                                                        # 3:retain
                                                        # 4:string 5:weak
        self.is_addable             = bool(addable)
        self.is_removable           = bool(removable)
        self.is_raisable            = bool(raisable)
        # # from doxygen sqlite3gen.cpp:
        # # 0:define 1:function 2:variable 3:typedef 4:enum 5:enumvalue
        # # 6:signal 7:slot 8:friend 9:DCOP 10:property 11:event
        self.kind                   = kind
        self.bodystart              = bodystart
        self.bodyend                = bodyend
        self.id_bodyfile            = id_bodyfile
        self.id_file                = id_file
        self.start_line             = start_line
        self.start_col              = start_col
        self.inherited_from         = inherited_from
        self.compound_id            = compound_id       # ID of parent compound
        self.compound_kind          = compound_kind     # its kind
        self.filename               = filename
        self.language               = language
        self.args                   = args
        self.doc_block              = DocBlock(*other)

    def __str__(self):
        return '<Definition:%s>' % self.name

    def get_start_pos(self):
        """Get start position of the definition or its docstring.

        Returns:
            tuple: ``(line, column)``.
        """
        if self.doc_block.start_line is not None:
            return self.doc_block.start_line, self.doc_block.start_col
        return self.start_line, self.start_col

    @property
    def is_method(self):
        return self.compound_kind == 'class'


class ContentDb:
    """This class represents content database."""
    def __init__(self, context, filename):
        self.context = context
        self.filename = filename
        self._conn = None

    @property
    def conn(self):
        if self._conn is None:
            self._conn = sqlite3.connect(self.filename)
        return self._conn

    def finalize(self):
        self.conn.commit()

    def get_definitions(self):
        res = self.conn.execute("""SELECT
        m.rowid, m.refid, m.name, m.definition, m.type, m.argsstring, m.scope,
        m.initializer, m.bitfield, m.read, m.write, m.prot, m.static, m.const,
        m.explicit, m.inline, m.final, m.sealed, m.new, m.optional, m.required,
        m.volatile, m.virt, m.mutable, m.initonly, m.attribute, m.property,
        m.readonly, m.bound, m.constrained, m.transient, m.maybevoid,
        m.maybedefault, m.maybeambiguous, m.readable, m.writable, m.gettable,
        m.privategettable, m.protectedgettable, m.settable, m.privatesettable,
        m.protectedsettable, m.accessor, m.addable, m.removable, m.raisable,
        m.kind, m.bodystart, m.bodyend, m.id_bodyfile, m.id_file, m.line,
        m.column, m.inherited_from, m.id_compound, c.kind,
        f.name,f.language,
        d.rowid, d.id_member, d.kind, d.id_file, d.start_line, d.start_col,
        d.end_line, d.end_col, d.docstring, d.doc              
        FROM memberdef m
        LEFT JOIN files f ON f.rowid=m.id_file
        LEFT JOIN docblocks d ON d.id_member=m.rowid
        LEFT JOIN compounddef c ON m.id_compound = c.rowid
        """)

        for row in res:
            # Get definition args.
            # NOTE: currently it can't detect specified types.
            arg_res = self.conn.execute("""SELECT p.defname, p.declname, p.type
            FROM memberdef_params m LEFT JOIN params p ON m.id_param=p.rowid
            WHERE m.id_memberdef=%d ORDER BY m.rowid
            """ % row[0])
            # NOTE: '**kwargs' is stored as (similar for *args):
            # defname = NULL, declname='kwargs`, type='**'
            args = tuple(Arg(x[2] + x[1], None) if x[1] else Arg(x[0], None)
                         for x in arg_res)
            d = Definition(args, *row)
            yield d

    # TODO: save by chunks in transaction.
    def save_doc_block(self, definition):
        doc = definition.doc_block
        if doc.id is None:
            self.conn.execute("""INSERT INTO docblocks
            (id_member,kind,id_file,start_line,start_col,end_line,end_col,
            docstring,doc)
            VALUES (?,?,?,?,?,?,?,?,?)
            """, (
                doc.id_member,
                doc.kind,
                doc.id_file,
                doc.start_line,
                doc.start_col,
                doc.end_line,
                doc.end_col,
                doc.docstring,
                None  # doc.document
            ))
        else:
            self.conn.execute("""
            UPDATE OR FAIL docblocks SET docstring = ? WHERE rowid=?
            """, (doc.docstring, definition.doc_block.id))

    def save_settings(self, settings):
        """Save settings in the DB."""
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS meta(name TEXT UNIQUE, value TEXT)
        """)
        self.conn.execute('INSERT OR REPLACE INTO meta VALUES(?,?)',
                          ('settings', json.dumps(settings)))

    def get_languages(self):
        """Get files languages.

        Returns:
            List of languages.
        """
        res = self.conn.execute('SELECT DISTINCT language FROM files')
        return [x[0] for x in res]

    def get_files_count(self):
        """Get number of files in DB."""
        res = self.conn.execute('SELECT count(*) FROM files').fetchone()
        return int(res[0])

    def get_domain_files(self, domain):
        """Get files supported by the given domain.

        Args:
            domain: Language domain.

        Yields:
            Tuples ``(file_id, filename)``.
        """
        res = self.conn.execute('SELECT rowid,name FROM files WHERE language=?',
                                (domain.name,))
        yield from res

    def get_doc_blocks(self, file_id):
        """Get doc blocks for the given file.

        Args:
            file_id: File ID.

        Yields:
            :class:`DocBlock` instances.
        """
        res = self.conn.execute("""
        SELECT rowid, id_member, kind, id_file, start_line,
        start_col, end_line, end_col, docstring FROM docblocks WHERE id_file=?
        """, (file_id,))

        for row in res:
            yield DocBlock(*row, None)

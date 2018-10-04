import os
import os.path as op
import sys
import sqlite3
import subprocess
import tempfile
import json
import enum
from collections import namedtuple


class ContentDbError(Exception):
    """Content DB error."""
    pass


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
    """Documentation block."""
    __slots__ = ['id', 'refid', 'type', 'id_file', 'start_line',
                 'start_col', 'end_line', 'end_col', 'docstring', 'document']

    def __init__(self, rowid, refid, type, id_file, start_line, start_col,
                 end_line, end_col, docstring, doc):
        self.id = rowid
        self.refid = refid
        self.type = type
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


#: :class:`MemberDefinition` argument.
#:
#: Attributes:
#:     name: Argument name.
#:     type_list: List of possible argument types.
#:
Arg = namedtuple('Arg', ['name', 'type_list'])
_empty_args = ()


class TypeEnum(enum.IntEnum):
    """Base class for type enums."""

    @classmethod
    def from_(cls, val):
        """Create enum instance from the given value.

        Args:
            val: Integer or ``None``.

        Returns:
            :class:`TypeEnum` instance or ``None`` if ``val`` is ``None``.
        """
        return cls(val) if val is not None else None


# NOTE: values reflects the ones from the doxygen's 'DefinitionIntf.DefType'.
class DefinitionType(TypeEnum):
    """This enum provides :class:`Definition` types."""

    #: Class definition.
    CLASS = 0

    # NOTE: not supported yet.
    # FILE = 1
    # NAMESPACE = 2

    #: Member definition like attribute, function or method.
    #:
    #: See :attr:`MemberDefinition.kind` for full list
    MEMBER = 3

    #: NOTE: not supported yet.
    # GROUP = 4
    # PACKAGE = 5
    # PAGE = 6
    # DIR = 7
    # SYMBOL_LIST = 8


# NOTE: values reflects the ones from the doxygen's 'ClassDef.CompoundType'.
class CompoundType(TypeEnum):
    """This enum provides :class:`CompoundDefinition` type."""
    CLASS = 0
    STRUCT = 1
    UNION = 2
    INTERFACE = 3
    PROTOCOL = 4
    CATEGORY = 5
    EXCEPTION = 6
    SERVICE = 7
    SINGLETON = 8


# NOTE: values reflects the ones from the doxygen's 'MemberType'.
class MemberType(TypeEnum):
    """This enum provides :class:`MemberDefinition` type."""
    DEFINE = 0
    FUNCTION = 1
    VARIABLE = 2
    TYPEDEF = 3
    ENUMERATION = 4
    ENUMVALUE = 5
    SIGNAL = 6
    SLOT = 7
    FRIEND = 8
    DCOP = 9
    PROPERTY = 10
    EVENT = 11
    INTERFACE = 12
    SERVICE = 13


class Definition:
    """Base definition class.

    Args:
        type: Definition type.
        id: Definition ID.
        refid: Definition reference ID.
        name: Definition name.
        language: Definition language.
        filename: Filename where definition is palced.
        doc_block: Definition documentation block :class:`DocBlock`.
    """
    __slots__ = ['type', 'id', 'refid', 'name', 'language', 'id_file',
                 'filename', 'doc_block', 'start_line', 'start_col']

    def __init__(self, type, id, refid, name, language, id_file, filename,
                 doc_block, start_line, start_col):
        self.type = type
        self.id = id
        self.refid = refid
        self.name = name
        self.language = language
        self.filename = filename
        self.id_file = id_file
        self.doc_block = doc_block
        self.start_line = start_line
        self.start_col = start_col

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


class CompoundDefinition(Definition):
    """This class represents a compound definition (like class or struct)."""
    __slots__ = ['compound_type', 'args']

    def __init__(self, id, refid, name, language, id_file, filename,
                 start_line, start_col, compound_type, doc_block):
        super(CompoundDefinition, self).__init__(
            DefinitionType.CLASS, id, refid, name, language, id_file, filename,
            doc_block, start_line, start_col)
        self.compound_type = CompoundType.from_(compound_type)

        # Optional constructor args.
        self.args = None


class MemberDefinition(Definition):
    """This class represents member definition (like function or method)."""
    __slots__ = ['member_type', 'scope', 'initializer', 'read', 'write',
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
                 'id_bodyfile', 'inherited_from', 'compound_id',
                 'compound_type', 'args']

    def __init__(self, id, refid, name, language, id_file, filename,
                 start_line, start_col, member_type, scope, initializer, read,
                 write, visibility, is_static, is_const, is_explicit, is_inline,
                 is_final, is_sealed, is_new, is_optional, is_required,
                 is_volatile, virtual, is_mutable, is_initonly, is_attribute,
                 is_property, is_readonly, is_bound, is_constrained,
                 is_transient, is_maybevoid, is_maybedefault, is_maybeambiguous,
                 is_readable, is_writable, is_gettable, is_privategettable,
                 is_protectedgettable, is_settable, is_privatesettable,
                 is_protectedsettable, accessor, is_addable, is_removable,
                 is_raisable, kind, bodystart, bodyend, id_bodyfile,
                 inherited_from, compound_id, compound_type, doc_block, args):
        super(MemberDefinition, self).__init__(
            DefinitionType.MEMBER,id, refid, name, language, id_file, filename,
            doc_block, start_line, start_col)
        self.member_type = member_type
        self.scope = scope
        self.initializer = initializer
        self.read = read
        self.write = write
        # 0:public 1:protected
        # 2:private 3:package
        self.visibility = visibility
        self.is_static = bool(is_static)
        self.is_const = bool(is_const)
        self.is_explicit = bool(is_explicit)
        self.is_inline = bool(is_inline)
        self.is_final = bool(is_final)
        self.is_sealed = bool(is_sealed)
        self.is_new = bool(is_new)
        self.is_optional = bool(is_optional)
        self.is_required = bool(is_required)
        self.is_volatile = bool(is_volatile)
        # 0:no 1:virtual
        # 2:pure-virtual
        self.virtual = virtual
        self.is_mutable = bool(is_mutable)
        self.is_initonly = bool(is_initonly)
        self.is_attribute = bool(is_attribute)
        self.is_property = bool(is_property)
        self.is_readonly = bool(is_readonly)
        self.is_bound = bool(is_bound)
        self.is_constrained = bool(is_constrained)
        self.is_transient = bool(is_transient)
        self.is_maybevoid = bool(is_maybevoid)
        self.is_maybedefault = bool(is_maybedefault)
        self.is_maybeambiguous = bool(is_maybeambiguous)
        self.is_readable = bool(is_readable)
        self.is_writable = bool(is_writable)
        self.is_gettable = bool(is_gettable)
        self.is_privategettable = bool(is_privategettable)
        self.is_protectedgettable = bool(is_protectedgettable)
        self.is_settable = bool(is_settable)
        self.is_privatesettable = bool(is_privatesettable)
        self.is_protectedsettable = bool(is_protectedsettable)
        # 1:assign 2:copy
        # 3:retain
        # 4:string 5:weak
        self.accessor = accessor
        self.is_addable = bool(is_addable)
        self.is_removable = bool(is_removable)
        self.is_raisable = bool(is_raisable)
        # from doxygen sqlite3gen.cpp:
        # 0:define 1:function 2:variable 3:typedef 4:enum 5:enumvalue
        # 6:signal 7:slot 8:friend 9:DCOP 10:property 11:event
        self.kind = MemberType.from_(kind)
        self.bodystart = bodystart
        self.bodyend = bodyend
        self.id_bodyfile = id_bodyfile
        self.inherited_from = inherited_from
        # ID of parent compound and its type.
        self.compound_id = compound_id
        self.compound_type = CompoundType.from_(compound_type)
        self.filename = filename
        self.language = language
        self.args = args

    def __str__(self):
        return '<MemberDefinition:%s>' % self.name

    # TODO: test me
    @property
    def is_function(self):
        """``True`` if this member is a function."""
        return self.kind in (MemberType.FUNCTION, MemberType.SIGNAL,
                             MemberType.FRIEND, MemberType.DCOP,
                             MemberType.SLOT)

    # TODO: test me
    @property
    def is_method(self):
        """``True`` if this member is a class method."""
        if self.kind is MemberType.FUNCTION and self.compound_type in (
                CompoundType.CLASS, CompoundType.STRUCT,
                CompoundType.INTERFACE):
            return True
        elif self.kind in (MemberType.SIGNAL, MemberType.SLOT):
            return True
        return False


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

    def get_compound_definitions(self, rowid=None):
        """Get compound definitions from the DB.

        Args:
            rowid: Optional definition ID in the DB. If not specified then
            yields all definitions. Otherwise *returns* single definition with
            the specified ``rowid``.

        Yields:
            :class:`CompoundDefinition`

        Returns:
            :class:`CompoundDefinition` with specified `rowid` or ``None``.
        """
        sql = """SELECT 
        c.rowid, c.refid, c.name, f.language, c.id_file, f.name,
        c.line, c.column, c.kind_id,        
        d.rowid, d.refid, d.type, d.id_file, d.start_line, d.start_col,
        d.end_line, d.end_col, d.docstring, d.doc
        FROM compounddef c
        LEFT JOIN files f ON f.rowid=c.id_file
        LEFT JOIN docblocks d ON d.refid=c.refid
        """

        if rowid is None:
            sql += ' WHERE c.id_file != -1'
        else:
            sql += ' WHERE c.rowid = %d' % rowid

        for row in self.conn.execute(sql):
            doc = DocBlock(*row[-10:])
            definition = CompoundDefinition(*row[:-10], doc)
            if rowid is not None:
                return definition
            yield definition

    def get_args(self, rowid):
        """Get member definition args.

        Args:
            rowid: Member definition ID.

        Returns:
            Tuple of args.
        """
        # NOTE: currently it can't detect specified types.
        arg_res = self.conn.execute("""SELECT p.type, p.declname, p.defname
            FROM memberdef_params m LEFT JOIN params p ON m.id_param=p.rowid
            WHERE m.id_memberdef=%d ORDER BY m.rowid
            """ % rowid)
        # NOTE: '**kwargs' is stored as (similar for *args):
        # type='**', declname='kwargs`, defname = NULL
        tl = ('**', '*')
        args = tuple(Arg(x[0] + x[1], None)
                     if x[0] in tl else Arg(x[2], None)
                     for x in arg_res)
        return args

    def get_constructor(self, compound_id):
        """Get constructor definition for the given compound (class, struct).

        Args:
            compound_id: Compound ID.

        Returns:
            :class:`MemberDefinition` or ``None``.

        See Also:
            :meth:`get_member_definitions`.
        """
        gen = self.get_member_definitions(name='__init__', compound=compound_id)
        return next(gen, None)

    def get_member_definitions(self, name=None, compound=None):
        """Get member definitions from the DB.

        ``name`` and ``compound`` are used to get specific member definition
        (both values must be specified).

        Args:
            name: Optional definition name.
            compound: Optional parent compound ID.

        Yields:
            :class:`MemberDefinition`
        """
        sql = """SELECT
        m.rowid, m.refid, m.name, f.language, m.id_file, f.name,
        m.line, m.column, m.type, m.scope, m.initializer, m.read, m.write,
        m.prot, m.static, m.const,
        m.explicit, m.inline, m.final, m.sealed, m.new, m.optional, m.required,
        m.volatile, m.virt, m.mutable, m.initonly, m.attribute, m.property,
        m.readonly, m.bound, m.constrained, m.transient, m.maybevoid,
        m.maybedefault, m.maybeambiguous, m.readable, m.writable, m.gettable,
        m.privategettable, m.protectedgettable, m.settable, m.privatesettable,
        m.protectedsettable, m.accessor, m.addable, m.removable, m.raisable,
        m.kind, m.bodystart, m.bodyend, m.id_bodyfile, 
        m.inherited_from, m.id_compound, c.kind_id,
        d.rowid, d.refid, d.type, d.id_file, d.start_line, d.start_col,
        d.end_line, d.end_col, d.docstring, d.doc              
        FROM memberdef m
        LEFT JOIN files f ON f.rowid=m.id_file
        LEFT JOIN docblocks d ON d.refid=m.refid
        LEFT JOIN compounddef c ON m.id_compound = c.rowid
        """
        if name and compound:
            sql += ' WHERE m.name = "%s" AND m.id_compound = %d' % (name,
                                                                    compound)

        for row in self.conn.execute(sql):
            doc = DocBlock(*row[-10:])
            args = self.get_args(row[0])
            definition = MemberDefinition(*row[:-10], doc, args)
            yield definition

    def get_definitions(self):
        """Get definitions from the DB.

        At first, this method yields compound definitions and then member
        definitions.

        Yields:
            :class:`Definition` instances.
        """
        yield from self.get_compound_definitions()
        yield from self.get_member_definitions()

    # TODO: save by chunks in transaction.
    def save_doc_block(self, definition):
        doc = definition.doc_block
        if doc.id is None:
            self.conn.execute("""INSERT INTO docblocks
            (refid,type,id_file,start_line,start_col,end_line,end_col,
            docstring,doc)
            VALUES (?,?,?,?,?,?,?,?,?)
            """, (
                doc.refid,
                doc.type,
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
        SELECT rowid, refid, type, id_file, start_line, start_col,
        end_line, end_col, docstring FROM docblocks WHERE id_file=?
        """, (file_id,))

        for row in res:
            yield DocBlock(*row, None)

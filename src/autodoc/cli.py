import sys
import click

if __name__ == '__main__':
    # If sys.frozen is defined then we packed with cx_Freeze and
    # module path modification is not required.
    if not getattr(sys, 'frozen', False):
        import os.path as op
        sys.path.append(op.join(op.dirname(__file__), '..'))


from autodoc import __version__
from autodoc.errors import AutodocError
from autodoc.context import Context
from autodoc.report import create_logger
from autodoc.contentdb import ContentDbError
from autodoc.settings import SettingsBuilder


class SettingsOption(click.Option):
    """This Option adds its name to the :attr:`click.Context.obj` dict
    if not set in the command line.
    """
    def consume_value(self, ctx, opts):
        # Add name to the 'obj' if the param is not specified in the
        # command line.
        value = click.Option.consume_value(self, ctx, opts)
        if self.name in opts:
            if ctx.obj is None:
                ctx.obj = {}
            settings = ctx.obj.setdefault('settings', {})
            settings[self.name] = value
        return value


def get_content_db(context, paths, exclude, exclude_patterns, exe, db_filename,
                   out):
    try:
        if db_filename is None:
            if not paths:
                raise click.ClickException(
                    'At least one path must be specified.')
            db = context.build_content_db(out, paths, exclude=exclude,
                                          exclude_patterns=exclude_patterns,
                                          exe=exe)
        else:
            db = context.get_content_db(db_filename)
    except ContentDbError as e:
        msg = str(e)
        if msg:
            raise click.ClickException(str(e))
        sys.exit(1)

    return db


def init(logger):
    from autodoc.python.domain import PythonDomain

    ctx = Context(logger)
    ctx.register(PythonDomain())

    return ctx


@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.version_option(version=__version__, message='%(version)s')
@click.option('--verbose', '-v', is_flag=True, default=False, show_default=True,
              help='Verbose output.', cls=SettingsOption)
@click.option('--fix/--no-fix', default=False, show_default=True,
              help='Auto fix detected issues.', cls=SettingsOption)
@click.option('--builder', '-b', metavar='EXE',
              type=click.Path(dir_okay=False, exists=True),
              help='Content DB builder executable.')
@click.option('--db', type=click.Path(dir_okay=False, exists=True),
              help='Content DB to process.')
@click.option('--out', '-o', type=click.Path(dir_okay=False),
              default='content.db', show_default=True,
              help='Output content DB.')
@click.option('--exclude', '-e', multiple=True, metavar='PATH',
              help='Files and/or dirs to exclude.')
@click.option('--exclude-pattern', '-x', multiple=True, metavar='WILDCARD',
              help='Exclude pattern.')
@click.option('--config', '-c', help='Configuration file.',
              type=click.Path(dir_okay=False, exists=True))
@click.option('--dump-settings', is_flag=True, default=False,
              help='Dump settings and exit.')
@click.option('-s', help='Overwrite a setting.', metavar='VAR=VALUE',
              multiple=True)
@click.argument('path', type=click.Path(exists=True), nargs=-1)
@click.pass_context
def cli(ctx, verbose, fix, builder, db, out, exclude, exclude_pattern, config,
        dump_settings, s, path):
    """Autodoc tool."""

    logger = create_logger(verbose)
    context = init(logger)

    settings_builder = SettingsBuilder()
    settings_builder.collect(context)

    if config:
        settings_builder.load_config(config)
    settings_builder.add_from_keyvalues(s)

    if dump_settings:
        settings_builder.dump(sys.stdout)
        return

    context.settings = settings_builder.get_settings()

    content_db = get_content_db(context, paths=path, exclude=exclude,
                                exclude_patterns=exclude_pattern,
                                exe=builder, db_filename=db, out=out)

    try:
        context.analyze(content_db)
        content_db.save_settings(settings_builder.settings)
        content_db.finalize()
    except AutodocError as e:
        raise click.ClickException(str(e))


if __name__ == '__main__':
    cli()
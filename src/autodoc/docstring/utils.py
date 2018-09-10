def nop(*args, **kwargs):
    pass


def need_blank(opt, lines):
    """Helper function to get blank line flag.

    Returns True if:

    * ``opt`` is ``True``
    * ``opt`` is ``None`` and ``lines`` has more than one line.

    Args:
        opt: Option.
        lines: Block lines.

    Returns:
        Boolean value.
    """
    return opt is True or (opt is None and len(lines) > 1)


def get_role_part(rawsource):
    """Helper function to get role name from the instruction.

    Args:
        rawsource: Role raw text.

    Example:

        :role:`text` -> :role:`
    """
    return rawsource[:rawsource.find('`') + 1]


def get_target_name(node):
    """Helper function to extract text from the directive:

          .. _<text>:

    """
    txt = node.rawsource
    s = txt.index('_') + 1
    e = txt.index(':', s+1)
    return txt[s:e]


def add_report(node, code, message):
    reporter = node.document.env['reporter']
    if reporter is not None:
        reporter.add_report(code, message, 0, 0)

lambda x: xx

def write2(): pass


def write(*args, **kw):
    raise NotImplementedError


async def foo(one, *args, **kw):
    """
    Args:
    args: Test
    """
    data = yield from read_data(db)

def _simple_decorator(decorator):
    def new_decorator(f):
        g = decorator(f)
        g.__name__ = f.__name__
        g.__doc__ = f.__doc__
        g.__dict__.update(f.__dict__)
        return g
        # Now a few lines needed to make simple_decorator itself
        # be a well-behaved decorator.

    new_decorator.__name__ = decorator.__name__
    new_decorator.__doc__ = decorator.__doc__
    new_decorator.__dict__.update(decorator.__dict__)
    return new_decorator


@_simple_decorator
def disallow_none_args(func):
    """If the user ID is None, a ValueError is raised."""

    msg = 'Arguments cannot be None.'

    def verify_id(*args, **kwargs):
        if None in args:
            raise ValueError(msg)

        if None in kwargs.values():
            raise ValueError(msg)
        return func(*args, **kwargs)

    return verify_id

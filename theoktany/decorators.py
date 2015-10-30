from theoktany.user import User


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
def verify_user_id(func):
    """If the user ID is None, a ValueError is raised."""

    msg = 'User must have an OKTA id.'

    def verify_id(*args, **kwargs):
        for arg in args:
            if isinstance(arg, User):
                if not arg.id:
                    raise ValueError(msg)

        for arg in kwargs:
            if isinstance(arg, User):
                if not arg.id:
                    raise ValueError(msg)
        return func(*args, **kwargs)

    return verify_id


@_simple_decorator
def verify_user_phone_number(func):
    """If the user's phone number is None, a ValueError is raised."""

    msg = 'User must have an OKTA id.'

    def verify_phone_number(*args, **kwargs):
        for arg in args:
            if isinstance(arg, User):
                if not arg.phone_number:
                    raise ValueError(msg)

        for arg in kwargs:
            if isinstance(arg, User):
                if not arg.phone_number:
                    raise ValueError(msg)
        return func(*args, **kwargs)

    return verify_phone_number

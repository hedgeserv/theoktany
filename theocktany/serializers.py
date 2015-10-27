import json

from theocktany.exceptions import SerializerException
from theocktany.user import User


def serialize(value):
    """Default serializer"""
    return json.dumps(value)


def deserialize(value):
    """Default deserializer"""
    if not isinstance(value, str):
        raise SerializerException('Needs a string')
    try:
        return json.loads(value)
    except ValueError as err:
        raise SerializerException(err)

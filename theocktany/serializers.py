import json

from theocktany.exceptions import SerializerException


def serialize(obj):
    """The base JSON serializer

    :param obj: the object to serialize
    :type obj: object
    :return: A string with a JSON representation of the object.
    """
    return json.dumps(obj)


def deserialize(value):
    """The base JSON deserializer

    :param value: the JSON string to deserialize
    :type value: str
    :return: A Python dictionary of key-value pairs present in the JSON object.
    """
    if not isinstance(value, str):
        raise SerializerException('Needs a string')
    try:
        return json.loads(value)
    except ValueError as err:
        raise SerializerException(err)

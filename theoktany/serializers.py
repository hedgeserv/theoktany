import json


def serialize(obj):
    """The base JSON serializer"""
    return json.dumps(obj)


def deserialize(value, encoding='UTF-8'):
    """The base JSON deserializer"""
    if isinstance(value, bytes):
        value = value.decode(encoding)

    if not isinstance(value, str):
        return {}

    try:
        return json.loads(value)
    except ValueError:
        return {}

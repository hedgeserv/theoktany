import unittest

from theoktany.serializers import serialize


class SerializerTest(unittest.TestCase):

    class TestObject(object):
        def __init__(self, **kwargs):
            for name, value in kwargs.items():
                self.__setattr__(name, value)

    def test_serialize(self):
        object_dict = {'firstName': 'Test', 'lastName': 'Test last'}
        json_str1 = '"firstName": "Test"'
        json_str2 = '"lastName": "Test last"'
        serialized_str = serialize(object_dict)
        self.assertIn(json_str1, serialized_str)
        self.assertIn(json_str2, serialized_str)

    def test_serialize_string(self):
        """Ensure that quotes are properly escaped"""
        string = 'This is a "string" with \'quotes.\''
        json_string = '"{}"'.format(string.replace('"', '\\"'))
        self.assertEqual(serialize(string), json_string)

    def test_serialize_none(self):
        """Ensure that None gets serialized to 'null'"""
        self.assertEqual(serialize(None), 'null')

    def test_serialize_object(self):
        """Ensure that the serializer throws an error for an unserializable object"""
        test_obj = self.TestObject(prop1='x', prop2=1234)

        with self.assertRaises(TypeError):
            serialize(test_obj)


if __name__ == '__main__':
    unittest.main()

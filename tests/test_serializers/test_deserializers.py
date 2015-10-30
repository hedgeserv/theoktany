import unittest

from theoktany.serializers import deserialize


class DeserializerTest(unittest.TestCase):

    def test_deserialize(self):
        json_str = '{"firstname": "Test", "lastname": "Test last"}'
        user_dict = deserialize(json_str)

        self.assertIn('firstname', user_dict)
        self.assertEqual(user_dict['firstname'], 'Test')
        self.assertEqual(user_dict['lastname'], 'Test last')

    def test_deserialize_non_json(self):
        result = deserialize('<html></html>')
        self.assertTrue(isinstance(result, dict))
        self.assertEqual(len(result), 0)

    def test_deserialize_empty_string(self):
        result = deserialize('')
        self.assertTrue(isinstance(result, dict))
        self.assertEqual(len(result), 0)

    def test_deserialize_none(self):
        result = deserialize(None)
        self.assertTrue(isinstance(result, dict))
        self.assertEqual(len(result), 0)

    def test_deserialize_non_string(self):
        result = deserialize({'test': 'test'})
        self.assertTrue(isinstance(result, dict))
        self.assertEqual(len(result), 0)

    def test_deserialize_invalid_json(self):
        result = deserialize('{"test"}')
        self.assertTrue(isinstance(result, dict))
        self.assertEqual(len(result), 0)


if __name__ == '__main__':
    unittest.main()

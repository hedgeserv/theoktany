"""Tests for user"""

import unittest

from theocktany.serializers import deserialize
from theocktany.exceptions import SerializerException


class SerializerTest(unittest.TestCase):

    def test_deserialize(self):
        input = '{"firstname": "Test", "lastname": "Test last"}'
        user_dict = deserialize(input)

        self.assertIn('firstname', user_dict)
        self.assertEqual(user_dict['firstname'], 'Test')
        self.assertEqual(user_dict['lastname'], 'Test last')

    def test_error_deserialize(self):
        with self.assertRaises(SerializerException):
            deserialize('<html></html>')

        with self.assertRaises(SerializerException):
            deserialize('')

        with self.assertRaises(SerializerException):
            deserialize(None)

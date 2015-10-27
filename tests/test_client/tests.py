"""Tests for API client"""

import os
import unittest

from theocktany.conf import settings

# TODO: shair: this should get passed to mb_wrapper
MOUNTEBANK_URL = 'localhost:2525'
# TODO: look into javscript injection for mountebank matching


class TestSettings(unittest.TestCase):

    def test_global_settings(self):
        """Ensure that we can get values from global_settings"""

        try:
            settings.get('API_TOKEN')
        except AttributeError as err:
            raise AssertionError(err)

    def test_instance_settings(self):
        """Ensure that we can set and get instance settings"""

        settings.set('API_TOKEN', 1)
        self.assertEqual(settings.get('API_TOKEN'), 1)

    def test_environment_variable_setting(self):
        """Ensure that we can get settings from environment variables"""

        os.environ['THEOKTANY_TEST_VAR'] = '1'
        try:
            value = settings.get('TEST_VAR')
            self.assertEqual(value, '1')
        except AttributeError as err:
            raise AssertionError(err)


if __name__ == '__main__':
    unittest.main()

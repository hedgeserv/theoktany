"""Tests for API client"""

from importlib import reload    # this is Python 3 specific
import os
import unittest
from unittest.mock import MagicMock

import requests

import theoktany
from theoktany import ApiClient
from theoktany.conf import settings
from theoktany.exceptions import ApiException
from tests.mb_wrapper import MountebankProcess


class TestSettings(unittest.TestCase):

    def tearDown(self):
        # get rid of all of our custom settings and environment variables
        reload(theoktany.conf)

        to_delete = []
        for var_name in os.environ:
            if 'THEOKTANY_' in var_name:
                to_delete.append(var_name)

        for var_name in to_delete:
            os.environ.pop(var_name)

    def test_global_settings(self):
        """Ensure that we can get values from global_settings"""

        try:
            settings.get('API_TOKEN')
        except AttributeError as err:
            raise AssertionError(err)

    def test_instance_settings(self):
        """Ensure that we can set and get instance settings"""

        settings.set('API_TOKEN', '1')
        self.assertEqual(settings.get('API_TOKEN'), '1')

    def test_environment_variable_setting(self):
        """Ensure that we can get settings from environment variables"""

        os.environ['THEOKTANY_TEST_VAR'] = '1'
        try:
            value = settings.get('TEST_VAR')
            self.assertEqual(value, '1')
        except AttributeError as err:
            raise AssertionError(err)


class TestResponses(unittest.TestCase):

    def setUp(self):
        self.mb = MountebankProcess()

    def tearDown(self):
        self.mb.destroy_all_imposters()

    def test_no_response(self):
        """Ensure that API client handles no response from the server gracefully"""
        api_client = ApiClient(BASE_URL='http://example.com', API_TOKEN='dummy')

        # fake out the requests.get method
        requests.get = MagicMock(return_value=None)
        response, status_code = api_client.get('/')
        self.assertIsNone(response)
        self.assertIsNone(status_code)

        # fake out the requests.post method
        requests.post = MagicMock(return_value=None)
        response, status_code = api_client.post('/')
        self.assertIsNone(response)
        self.assertIsNone(status_code)

        # reload requests so that the methods are back to normal
        reload(requests)

    def test_non_json_response(self):
        """Ensure that the API client handles non-JSON responses gracefully"""

        imposter = self.mb.create_imposter('test_api_client/stubs/test_client_response.json')
        api_client = ApiClient(BASE_URL=self.mb.get_imposter_url(imposter), API_TOKEN='dummy')

        response, _ = api_client.get('/non-json')
        self.assertEqual('<html><body><h1>Testing!</h1></body></html>', response)
        response, _ = api_client.post('/non-json')
        self.assertEqual('<html><body><h1>Testing!</h1></body></html>', response)

    def test_check_api_response_no_causes(self):
        api_client = ApiClient()

        err_msg = {
            "errorSummary": "This is a short error message",
            "errorCauses": []
        }
        try:
            api_client.check_api_response(err_msg, 400)
            raise AssertionError("check_api_response should have raised an exception and didn't.")
        except ApiException as err:
            self.assertIn(err_msg['errorSummary'], str(err))

    def test_check_api_response_with_causes(self):
        api_client = ApiClient()

        err_msg = {
            "errorSummary": "This is a short error message",
            "errorCauses": [
                {
                    "errorSummary": "This is a more detailed error message"
                },
                {
                    "errorSummary": "This is a second error"
                }
            ]
        }
        try:
            api_client.check_api_response(err_msg, 400)
            raise AssertionError("check_api_response should have raised an exception and didn't.")
        except ApiException as err:
            self.assertIn(err_msg['errorCauses'][0]['errorSummary'], str(err))

    def test_check_api_response_without_okta_error(self):
        """Ensure that an invalid response without an OKTA error gets handled properly"""

        api_client = ApiClient()
        try:
            api_client.check_api_response({}, 400)
            raise AssertionError("check_api_response should have raised an exception and didn't.")
        except ApiException as err:
            self.assertIn('Okta returned 400', str(err))


if __name__ == '__main__':
    unittest.main()
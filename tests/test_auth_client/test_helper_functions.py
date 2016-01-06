from unittest import TestCase

# noinspection PyProtectedMember
from theoktany.auth_client import _get_qr_code_from_response, _get_shared_secret_from_response, _validate

from tests.mb_wrapper import MountebankProcess


class ValidateTests(TestCase):
    def test_validate_200(self):
        response1 = {'key': 'value'}
        status_code = 200

        response2, message, error_code = _validate(response1, status_code)

        self.assertIs(response1, response2)
        self.assertEqual('Success', message)
        self.assertIsNone(error_code)

    def test_validate_201(self):
        response1 = {'key': 'value'}
        status_code = 201

        response2, message, error_code = _validate(response1, status_code)

        self.assertIs(response1, response2)
        self.assertEqual('Success', message)
        self.assertIsNone(error_code)

    def test_validate_202(self):
        response1 = {'key': 'value'}
        status_code = 202

        response2, message, error_code = _validate(response1, status_code)

        self.assertIs(response1, response2)
        self.assertEqual('Success', message)
        self.assertIsNone(error_code)

    def test_validate_204(self):
        response1 = {'key': 'value'}
        status_code = 204

        response2, message, error_code = _validate(response1, status_code)

        self.assertIs(response1, response2)
        self.assertEqual('Success', message)
        self.assertIsNone(error_code)

    def test_validate_400_error_summary_and_error_code(self):
        response1 = {
            'errorCauses': [
                {
                    'errorSummary': 'some_error'
                }
            ],
            'errorCode': 1234,
        }
        status_code = 400

        response2, message, error_code = _validate(response1, status_code)

        self.assertFalse(response2)
        self.assertEqual(response1['errorCauses'][0]['errorSummary'], message)
        self.assertEqual(response1['errorCode'], error_code)

    def test_validate_400_error_summary_no_error_code(self):
        response1 = {
            'errorCauses': [
                {
                    'errorSummary': 'some_error'
                }
            ],
        }
        status_code = 400

        response2, message, error_code = _validate(response1, status_code)

        self.assertFalse(response2)
        self.assertEqual(response1['errorCauses'][0]['errorSummary'], message)
        self.assertIsNone(error_code)

    def test_validate_400_no_error_cause_and_error_code(self):
        response1 = {
            'errorSummary': 'some other error',
            'errorCode': 1234,
        }
        status_code = 400

        response2, message, error_code = _validate(response1, status_code)

        self.assertFalse(response2)
        self.assertEqual(response1['errorSummary'], message)
        self.assertEqual(response1['errorCode'], error_code)

    def test_validate_400_no_error(self):
        response1 = {
            'errorCode': 1234,
        }
        status_code = 400

        response2, message, error_code = _validate(response1, status_code)

        self.assertFalse(response2)
        self.assertEqual('Okta returned 400.', message)

    def test_validate_400__error_cause_no_summary(self):
        response1 = {
            'errorCauses': [
                {}
            ],
            'errorCode': 1234,
        }
        status_code = 400

        response2, message, error_code = _validate(response1, status_code)

        self.assertFalse(response2)
        self.assertEqual('Okta returned 400.', message)


class GetQRCodeTests(TestCase):
    def setUp(self):
        self.mb = MountebankProcess()

    def tearDown(self):
        self.mb.destroy_all_imposters()

    def setup_imposter(self, file_name):
        port = self.mb.create_imposter('test_auth_client/stubs/' + file_name)
        return self.mb.get_imposter_url(port)

    def test_happy_path(self):
        imposter_url = self.setup_imposter('test_qr_code.json')
        response = {
            '_embedded': {
                'activation': {
                    '_links': {
                        'qrcode': {
                            'href': imposter_url
                        }
                    }
                }
            }
        }

        qr_code = _get_qr_code_from_response(response)
        self.assertIsNotNone(qr_code)

    def test_missing_qr_code_link(self):
        response = {
            '_embedded': {
                'activation': {
                    '_links': {
                        'qrcode': {}
                    }
                }
            }
        }

        qr_code = _get_qr_code_from_response(response)
        self.assertIsNone(qr_code)

    def test_bad_link(self):
        response = {
            '_embedded': {
                'activation': {
                    '_links': {
                        'qrcode': {
                            'href': 'http://localhost:1/asdf'
                        }
                    }
                }
            }
        }

        qr_code = _get_qr_code_from_response(response)
        self.assertIsNone(qr_code)


class GetSharedSecretTests(TestCase):

    def test_happy_path(self):
        response = {
            '_embedded': {
                'activation': {
                    'sharedSecret': 'some-secret'
                }
            }
        }

        secret = _get_shared_secret_from_response(response)
        self.assertEqual(response['_embedded']['activation']['sharedSecret'], secret)

    def test_missing_secret(self):
        response = {
            '_embedded': {
                'activation': {}
            }
        }

        secret = _get_shared_secret_from_response(response)
        self.assertIsNone(secret)

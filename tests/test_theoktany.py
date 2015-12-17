import unittest
from theoktany.auth_client import _validate as validate


class ValidationTest(unittest.TestCase):

    def test_successful_response(self):
        response_to_validate = {"happy": "joy"}
        response, message, error_code = validate(response_to_validate, 200)
        self.assertEqual(response_to_validate, response)
        self.assertEqual("Success", message)
        self.assertIsNone(error_code)

    def test_error_response_with_error_causes(self):
        response_to_validate = {"errorCode": "2", "errorCauses": [{'errorSummary': "message"}]}
        response, message, error_code = validate(response_to_validate, 404)
        self.assertFalse(response)
        self.assertEqual("message", message)
        self.assertEqual(error_code, '2')

    def test_error_response_with_only_error_summary(self):
        response_to_validate = {'errorSummary': "message"}
        response, message,error_code = validate(response_to_validate, 404)
        self.assertFalse(response)
        self.assertEqual("message", message)
        self.assertIsNone(error_code)

    def test_error_response_with_no_error_message(self):
        response, message, error_code = validate({}, 404)
        self.assertFalse(response)
        self.assertEqual("Okta returned 404.", message)
        self.assertIsNone(error_code)

import unittest
from theoktany.validate import validate


class ValidationTest(unittest.TestCase):

    def test_successful_response(self):
        response_to_validate = {"happy": "joy"}
        response, message = validate(response_to_validate, 200)
        self.assertEqual(response_to_validate, response)
        self.assertEqual("Success", message)

    def test_error_response_with_error_causes(self):
        response_to_validate = {"errorCauses": [{'errorSummary': "message"}]}
        response, message = validate(response_to_validate, 404)
        self.assertFalse(response)
        self.assertEqual("message", message)

    def test_error_response_with_only_error_summary(self):
        response_to_validate = {'errorSummary': "message"}
        response, message = validate(response_to_validate, 404)
        self.assertFalse(response)
        self.assertEqual("message", message)

    def test_error_response_with_no_error_message(self):
        response, message = validate({}, 404)
        self.assertFalse(response)
        self.assertEqual("Okta returned 404.", message)
import unittest

from theocktany import validate

class ValidationTest(unittest.TestCase):

    def test_200(self):
        response = {"happy": "joy"}
        self.assertTrue(validate(response, 200))


    def test_sad_with_error(self):
        response = {"errorCauses" : [{'errorSummary' : "message"}]}
        f, msg = validate(response, 404)
        self.assertFalse(f)
        self.assertEqual("message", msg)

    def test_sad_no_error(self):
        response = {'errorSummary' : "message"}
        f, msg = validate(response, 404)
        self.assertFalse(f)
        self.assertEqual("message", msg)

    def test_okta_having_a_sad(self):
        f, msg = validate({}, 404)
        self.assertFalse(f)
        self.assertEqual("Okta returned 404.", msg)
    
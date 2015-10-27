import unittest

from theocktany.auth_client import OktaAuthClient
from theocktany.client import ApiClient
from theocktany.exceptions import ApiException
from theocktany.user import User

from tests.mb_wrapper import MountebankProcess


class SMSAuthTests(unittest.TestCase):

    def setUp(self):
        self.api_client = ApiClient()
        self.auth_client = OktaAuthClient(self.api_client)
        self.mb = MountebankProcess()
        self.user = User('John', 'Doe', 'jdoe@example.com', phone_number='+1-555-555-5555', id='00u15s1KDETTQMQYABRL')

    def tearDown(self):
        self.mb.destroy_all_imposters()

    def test_user_attributes(self):
        """Ensure that user has OKTA ID and phone number"""

        user_without_id = self.user
        user_without_id.id = None

        with self.assertRaises(ValueError):
            self.auth_client.enroll_user_for_sms(user_without_id)

        user_without_phone_number = self.user
        user_without_phone_number.phone_number = None
        with self.assertRaises(ValueError):
            self.auth_client.enroll_user_for_sms(user_without_id)

    def test_sms_enrollment(self):
        """Ensure whether we are receiving proper response from OKTA"""

        imposter = self.mb.create_imposter('test_auth_client/stubs/test_sms_auth.json')
        api_client = ApiClient(BASE_URL=self.mb.get_imposter_url(imposter))
        auth_client = OktaAuthClient(api_client)

        try:
            auth_client.enroll_user_for_sms(self.user)
        except ApiException:
            raise AssertionError('SMS enrollment failed')

        with self.assertRaises(ApiException):
            self.auth_client.enroll_user_for_sms(self.user)

    def test_sms_enrollment_invalid_user_id(self):
        """Ensure whether proper error is thrown if invalid user id is passed"""
        # TODO: shair: look into matching POST data so that we can us the test_sms_auth.json predicate

        imposter = self.mb.create_imposter('test_auth_client/stubs/test_sms_auth_invalid_user_id.json')
        api_client = ApiClient(BASE_URL=self.mb.get_imposter_url(imposter))
        auth_client = OktaAuthClient(api_client)

        self.user.id = 'invalid_id'
        try:
            auth_client.enroll_user_for_sms(self.user)
        except ApiException as err:
            self.assertIn('invalid_id', str(err))

    def test_sms_enrollment_invalid_phone_number(self):
        """Ensure whether proper error is thrown if invalid phone number is passed"""
         # TODO: shair: look into matching POST data so that we can us the test_sms_auth.json predicate

        imposter = self.mb.create_imposter('test_auth_client/stubs/test_sms_auth_invalid_phone_number.json')
        api_client = ApiClient(BASE_URL=self.mb.get_imposter_url(imposter))
        auth_client = OktaAuthClient(api_client)

        self.user.phone_number = 'invalid_phone_number'
        try:
            auth_client.enroll_user_for_sms(self.user)
        except ApiException as err:
            self.assertIn('Invalid Phone Number', str(err))

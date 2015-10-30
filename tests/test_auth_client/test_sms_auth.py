import unittest

from theoktany.auth_client import OktaAuthClient
from theoktany.client import ApiClient
from theoktany.exceptions import ApiException, EnrollmentException
from theoktany.user import User

from tests.mb_wrapper import MountebankProcess


class SMSAuthTests(unittest.TestCase):

    def setUp(self):
        self.api_client = ApiClient()
        self.auth_client = OktaAuthClient(self.api_client)
        self.mb = MountebankProcess()
        self.user = User('John', 'Doe', 'jdoe@example.com', phone_number='+1-555-555-5555', id='00u15s1KDETTQMQYABRL')

    def tearDown(self):
        self.mb.destroy_all_imposters()

    def test_enrollment_user_attributes(self):
        """Ensure that user has OKTA ID and phone number"""

        user_without_id = self.user
        user_without_id.id = None

        with self.assertRaises(ValueError):
            self.auth_client.enroll_user_for_sms(user_without_id)
        with self.assertRaises(ValueError):
            self.auth_client.enroll_user_for_sms(user=user_without_id)

        user_without_phone_number = self.user
        user_without_phone_number.id = 'something'
        user_without_phone_number.phone_number = None
        with self.assertRaises(ValueError):
            self.auth_client.enroll_user_for_sms(user_without_phone_number)
        with self.assertRaises(ValueError):
            self.auth_client.enroll_user_for_sms(user=user_without_phone_number)

    def test_sms_enrollment(self):
        """Ensure whether we are receiving proper response from OKTA"""

        imposter = self.mb.create_imposter('test_auth_client/stubs/test_sms_enrollment.json')
        api_client = ApiClient(BASE_URL=self.mb.get_imposter_url(imposter), API_TOKEN='dummy')
        auth_client = OktaAuthClient(api_client)

        try:
            auth_client.enroll_user_for_sms(self.user)
        except ApiException:
            raise AssertionError('SMS enrollment failed')

        with self.assertRaises(ApiException):
            self.auth_client.enroll_user_for_sms(self.user)

    def test_sms_enrollment_invalid_user_id(self):
        """Ensure whether proper error is thrown if invalid user id is passed"""
        # TODO: shair: look into matching POST data so that we can us the test_sms_activation.json predicate

        imposter = self.mb.create_imposter('test_auth_client/stubs/test_sms_enrollment.json')
        api_client = ApiClient(BASE_URL=self.mb.get_imposter_url(imposter), API_TOKEN='dummy')
        auth_client = OktaAuthClient(api_client)

        self.user.id = 'invalid_id'
        try:
            auth_client.enroll_user_for_sms(self.user)
        except ApiException as err:
            self.assertIn('invalid_id', str(err))

    def test_sms_enrollment_invalid_phone_number(self):
        """Ensure whether proper error is thrown if invalid phone number is passed"""
        # TODO: shair: look into matching POST data so that we can us the test_sms_activation.json predicate

        imposter = self.mb.create_imposter('test_auth_client/stubs/test_sms_enrollment.json')
        api_client = ApiClient(BASE_URL=self.mb.get_imposter_url(imposter), API_TOKEN='dummy')
        auth_client = OktaAuthClient(api_client)

        self.user.phone_number = 'invalid_phone_number'
        try:
            auth_client.enroll_user_for_sms(self.user)
        except ApiException as err:
            self.assertIn('Invalid Phone Number', str(err))

    def test_activation_user_attributes(self):
        """Ensure that user has OKTA ID for sms factor activation"""

        user_without_id = self.user
        user_without_id.id = None

        with self.assertRaises(ValueError):
            self.auth_client.activate_sms_factor(user_without_id, None)

    def test_sms_activation_invalid_user_id(self):
        """Ensure whether proper error is thrown if invalid user id is passed during activation"""

        imposter = self.mb.create_imposter('test_auth_client/stubs/test_sms_activation.json')
        api_client = ApiClient(BASE_URL=self.mb.get_imposter_url(imposter), API_TOKEN='dummy')
        auth_client = OktaAuthClient(api_client)

        self.user.id = 'invalid_id'
        try:
            auth_client.activate_sms_factor(self.user, "1234567")
        except ApiException as err:
            self.assertIn('invalid_id', str(err))

    def test_sms_activation_user_not_enrolled(self):
        """Testing SMS factor activation for a user that isn't enrolled in sms authentication"""

        imposter = self.mb.create_imposter('test_auth_client/stubs/test_sms_activation.json')
        api_client = ApiClient(BASE_URL=self.mb.get_imposter_url(imposter), API_TOKEN='dummy')
        auth_client = OktaAuthClient(api_client)

        try:
            self.user.id = 'not-enrolled-in-sms'
            auth_client.activate_sms_factor(self.user, "123456")
            raise AssertionError("User was enrolled and shouldn't have been")
        except EnrollmentException as err:
            self.assertIn('User not associated with sms factor', str(err))

    def test_sms_activation_invalid_passcode(self):
        """Ensure that error is thrown if an invalid passcode is passed"""

        imposter = self.mb.create_imposter('test_auth_client/stubs/test_sms_activation.json')
        api_client = ApiClient(BASE_URL=self.mb.get_imposter_url(imposter), API_TOKEN='dummy')
        auth_client = OktaAuthClient(api_client)

        try:
            auth_client.activate_sms_factor(self.user, 'invalid-passcode')
            raise AssertionError("Passcode was valid and shouldn't have been")
        except ApiException as err:
            self.assertIn("passcode doesn't match our records", str(err))

    def test_sms_activation(self):
        """Test passcode activation and ensure that a user cannot be activated twice"""

        imposter = self.mb.create_imposter('test_auth_client/stubs/test_sms_activation.json')
        api_client = ApiClient(BASE_URL=self.mb.get_imposter_url(imposter), API_TOKEN='dummy')
        auth_client = OktaAuthClient(api_client)

        try:
            auth_client.activate_sms_factor(self.user, '123456')
        except ApiException:
            raise AssertionError("Passcode was invalid and shouldn't have been")

        try:
            auth_client.activate_sms_factor(self.user, '123456')
            raise AssertionError('User sms was activated twice')
        except ApiException as err:
            self.assertIn("Factor already exists.", str(err))

    def test_send_sms_user_attributes(self):
        """Ensure that user has OKTA ID for sms sending"""

        user_without_id = self.user
        user_without_id.id = None

        with self.assertRaises(ValueError):
            self.auth_client.send_sms_challenge(user_without_id)

    def test_send_sms_challenge_invalid_user_id(self):
        imposter = self.mb.create_imposter('test_auth_client/stubs/test_send_sms_challenge.json')
        api_client = ApiClient(BASE_URL=self.mb.get_imposter_url(imposter), API_TOKEN='dummy')
        auth_client = OktaAuthClient(api_client)

        self.user.id = 'invalid_id'
        try:
            auth_client.send_sms_challenge(self.user)
            raise AssertionError('User id was not invalid when it should have been')
        except ApiException as err:
            self.assertIn('invalid_id', str(err))

    def test_send_sms_challenge_unenrolled_user(self):
        imposter = self.mb.create_imposter('test_auth_client/stubs/test_send_sms_challenge.json')
        api_client = ApiClient(BASE_URL=self.mb.get_imposter_url(imposter), API_TOKEN='dummy')
        auth_client = OktaAuthClient(api_client)

        try:
            self.user.id = 'not-enrolled-in-sms'
            auth_client.send_sms_challenge(self.user)
            raise AssertionError('User is enrolled and should not have been.')
        except EnrollmentException as err:
            self.assertIn('User not associated with sms factor', str(err))

    def test_send_sms_challenge(self):
        imposter = self.mb.create_imposter('test_auth_client/stubs/test_send_sms_challenge.json')
        api_client = ApiClient(BASE_URL=self.mb.get_imposter_url(imposter), API_TOKEN='dummy')
        auth_client = OktaAuthClient(api_client)

        try:
            auth_client.send_sms_challenge(self.user)
        except ApiException as err:
            raise AssertionError('Sending SMS challenge failed: ' + str(err))

    def test_verify_sms_challenge_user_attributes(self):
        """Ensure that user has OKTA ID for sms sending"""

        user_without_id = self.user
        user_without_id.id = None

        with self.assertRaises(ValueError):
            self.auth_client.verify_sms_challenge_passcode(user_without_id, '123456')

    def test_verify_sms_challenge_invalid_user_id(self):
        imposter = self.mb.create_imposter('test_auth_client/stubs/test_verify_sms_challenge.json')
        api_client = ApiClient(BASE_URL=self.mb.get_imposter_url(imposter), API_TOKEN='dummy')
        auth_client = OktaAuthClient(api_client)

        self.user.id = 'invalid_id'
        try:
            auth_client.verify_sms_challenge_passcode(self.user, '123456')
            raise AssertionError('User id was not invalid when it should have been')
        except ApiException as err:
            self.assertIn('invalid_id', str(err))

    def test_verify_sms_challenge_invalid_passcode(self):
        imposter = self.mb.create_imposter('test_auth_client/stubs/test_verify_sms_challenge.json')
        api_client = ApiClient(BASE_URL=self.mb.get_imposter_url(imposter), API_TOKEN='dummy')
        auth_client = OktaAuthClient(api_client)

        try:
            auth_client.verify_sms_challenge_passcode(self.user, 'invalid-passcode')
            raise AssertionError("Passcode was valid and shouldn't have been")
        except ApiException as err:
            self.assertIn("passcode doesn't match our records", str(err))

    def test_verify_sms_challenge(self):
        imposter = self.mb.create_imposter('test_auth_client/stubs/test_verify_sms_challenge.json')
        api_client = ApiClient(BASE_URL=self.mb.get_imposter_url(imposter), API_TOKEN='dummy')
        auth_client = OktaAuthClient(api_client)

        try:
            auth_client.verify_sms_challenge_passcode(self.user, '123456')
        except ApiException:
            raise AssertionError("Passcode was invalid and shouldn't have been")

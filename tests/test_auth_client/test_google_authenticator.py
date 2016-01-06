from unittest import TestCase

from theoktany.auth_client import OktaAuthClient, OktaFactors
from theoktany.client import ApiClient

from tests.mb_wrapper import MountebankProcess


USER_ONE = {'id': '00001'}
USER_TWO = {'id': '00002'}
USER_THREE = {'id': '00003'}
USER_FOUR = {'id': '00004'}


class GoogleAuthenticatorTests(TestCase):
    def setUp(self):
        self.api_client = ApiClient()
        self.auth_client = OktaAuthClient(OktaFactors(self.api_client))
        self.mb = MountebankProcess()

    def tearDown(self):
        self.mb.destroy_all_imposters()

    def setup_imposter(self, file_name):
        port = self.mb.create_imposter('test_auth_client/stubs/' + file_name)
        imposter_url = self.mb.get_imposter_url(port)
        self.api_client.settings.set('BASE_URL', imposter_url)
        return imposter_url

    def test_enrollment_requirements(self):
        with self.assertRaises(AssertionError):
            self.auth_client.enroll_user_for_google_authenticator(None)

    def test_activation_requirements(self):
        with self.assertRaises(AssertionError):
            self.auth_client.activate_google_authenticator_factor(None, '123456')

        with self.assertRaises(AssertionError):
            self.auth_client.activate_google_authenticator_factor('0001', None)

    def test_verification_requirements(self):
        with self.assertRaises(AssertionError):
            self.auth_client.verify_google_authenticator_factor(None, '123456')

        with self.assertRaises(AssertionError):
            self.auth_client.verify_google_authenticator_factor('0001', None)

    def test_is_enrolled_requirements(self):
        with self.assertRaises(AssertionError):
            self.auth_client.is_user_enrolled_for_google_authenticator(None)

    def test_delete_requirements(self):
        with self.assertRaises(AssertionError):
            self.auth_client.delete_google_authenticator_factor(None)

    def test_enrollment_success(self):
        self.setup_imposter('test_google_authenticator_enrollment.json')

        response, message, error_code, extras = self.auth_client.enroll_user_for_google_authenticator(USER_ONE['id'])
        self.assertTrue(response)
        self.assertIsNotNone(response['id'])
        self.assertEqual('token:software:totp', response['factorType'])
        self.assertEqual('GOOGLE', response['provider'])
        self.assertEqual(message, "Success")
        self.assertIsNone(error_code)
        self.assertIn('shared_secret', extras)
        self.assertIsNotNone(extras['shared_secret'])
        self.assertIn('qr_code', extras)
        self.assertIsNotNone(extras['qr_code'])

    def test_enrollment_failure(self):
        self.setup_imposter('test_google_authenticator_enrollment.json')
        response, message, error_code, extras = self.auth_client.enroll_user_for_google_authenticator(USER_TWO['id'])
        self.assertFalse(response)
        self.assertEqual('Factor already exists.', message)
        self.assertIsNotNone(error_code)

    def test_activation_success(self):
        self.setup_imposter('test_google_authenticator_activation.json')
        response, message, error_code = self.auth_client.activate_google_authenticator_factor(USER_ONE['id'], '12345')
        self.assertTrue(response)
        self.assertEqual("Success", message)
        self.assertIsNone(error_code)

    def test_activation_failure_one(self):
        self.setup_imposter('test_google_authenticator_activation.json')
        response, message, error_code = self.auth_client.activate_google_authenticator_factor(USER_TWO['id'], '1')
        self.assertFalse(response)
        self.assertEqual("Your passcode doesn't match our records. Please try again.", message)
        self.assertEqual('E0000068', error_code)

    def test_activation_failure_two(self):
        self.setup_imposter('test_google_authenticator_activation.json')
        response, message, error_code = self.auth_client.activate_google_authenticator_factor(
            USER_THREE['id'], 'not-enrolled')
        self.assertFalse(response)
        self.assertEqual("Not enrolled in factor.", message)
        self.assertIsNotNone(error_code)

    def test_activation_failure_three(self):
        self.setup_imposter('test_google_authenticator_activation.json')
        response, message, error_code = self.auth_client.activate_google_authenticator_factor(
            USER_FOUR['id'], 'not-found')
        self.assertFalse(response)
        self.assertEqual("Not found: Resource not found: invalid_id (User)", message)
        self.assertIsNotNone(error_code)

    def test_verify_challenge_success(self):
        self.setup_imposter('test_google_authenticator_challenge.json')
        response, message, error_code = self.auth_client.verify_google_authenticator_factor(USER_ONE['id'], '12345')
        self.assertTrue(response)
        self.assertEqual(response.get('factorResult'), 'SUCCESS')
        self.assertEqual("Success", message)
        self.assertIsNone(error_code)

    def test_verify_challenge_failure_one(self):
        self.setup_imposter('test_google_authenticator_challenge.json')
        response, message, error_code = self.auth_client.verify_google_authenticator_factor(
            USER_ONE['id'], 'invalid-passcode')
        self.assertFalse(response)
        self.assertEqual("Your passcode doesn't match our records. Please try again.", message)
        self.assertEqual('E0000068', error_code)

    def test_verify_challenge_two(self):
        self.setup_imposter('test_google_authenticator_challenge.json')
        response, message, error_code = self.auth_client.verify_google_authenticator_factor(USER_THREE['id'], '12345')
        self.assertFalse(response)
        self.assertEqual("Not enrolled in factor.", message)

    def test_verify_challenge_failure_three(self):
        self.setup_imposter('test_google_authenticator_challenge.json')
        response, message, error_code = self.auth_client.verify_google_authenticator_factor(USER_FOUR['id'], '12345')
        self.assertFalse(response)
        self.assertEqual("Not found: Resource not found: invalid_id (User)", message)

    def test_user_is_enrolled(self):
        self.setup_imposter('test_google_authenticator_challenge.json')
        is_enrolled = self.auth_client.is_user_enrolled_for_google_authenticator(USER_ONE['id'])
        self.assertTrue(is_enrolled)

    def test_user_is_not_enrolled_in_pending_activation(self):
        self.setup_imposter('test_google_authenticator_challenge.json')
        is_enrolled = self.auth_client.is_user_enrolled_for_google_authenticator(USER_TWO['id'])
        self.assertFalse(is_enrolled)

    def test_user_is_not_enrolled_different_factor(self):
        self.setup_imposter('test_google_authenticator_challenge.json')
        is_enrolled = self.auth_client.is_user_enrolled_for_google_authenticator(USER_THREE['id'])
        self.assertFalse(is_enrolled)

    def test_user_is_not_enrolled_invalid_id(self):
        self.setup_imposter('test_google_authenticator_challenge.json')
        is_enrolled = self.auth_client.is_user_enrolled_for_google_authenticator("invalid_id")
        self.assertFalse(is_enrolled)

    def test_delete_factor(self):
        self.setup_imposter('test_google_authenticator_challenge.json')
        response, message, error_code = self.auth_client.delete_google_authenticator_factor(USER_ONE['id'])
        self.assertEqual(message, 'Success')
        self.assertIsNone(error_code)

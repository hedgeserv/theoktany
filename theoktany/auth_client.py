"""Wrapper for OKTA authentication calls"""
from theoktany.decorators import disallow_none_args
from theoktany.exceptions import EnrollmentException
from theoktany.serializers import serialize


class OktaAuthClient(object):
    """Client for interacting with OKTA's authentication system"""

    def __init__(self, api_client):
        self._api_client = api_client

    def _get_factor_id(self, user_id, factor_type="sms"):
        """Get the OKTA MFA factor ID"""

        response, status_code = self._api_client.get('/api/v1/users/{}/factors'.format(user_id))

        self._api_client.check_api_response(response, status_code)

        for factor in response:
            if factor['factorType'] == factor_type:
                return factor['id']
        else:
            raise EnrollmentException("User not associated with sms factor")

    @disallow_none_args
    def enroll_user_for_sms(self, user_id, phone_number):
        """Begin user enrollment process for SMS multi-factor authentication."""

        data = {
            "factorType": "sms",
            "provider": "OKTA",
            "profile": {
                "phoneNumber": phone_number
            }
        }
        response, status_code = self._api_client.post(
            '/api/v1/users/{}/factors'.format(user_id), data=serialize(data))

        self._api_client.check_api_response(response, status_code)

    @disallow_none_args
    def activate_sms_factor(self, user_id, passcode):
        """Activate the SMS authentication factor for a user."""

        factor_id = self._get_factor_id(user_id, 'sms')

        response, status_code = self._api_client.post(
            '/api/v1/users/{}/factors/{}/lifecycle/activate'.format(user_id, factor_id),
            data=serialize({'passCode': passcode}))

        self._api_client.check_api_response(response, status_code)

    @disallow_none_args
    def send_sms_challenge(self, user_id):
        """Send the SMS challenge to the user enrolled in SMS MFA."""

        factor_id = self._get_factor_id(user_id, 'sms')

        response, status_code = self._api_client.post('/api/v1/users/{}/factors/{}/verify'.format(user_id, factor_id))

        self._api_client.check_api_response(response, status_code)

    @disallow_none_args
    def verify_sms_challenge_passcode(self, user_id, passcode):
        """Verify that the user received the correct passcode."""

        factor_id = self._get_factor_id(user_id, 'sms')

        response, status_code = self._api_client.post(
            '/api/v1/users/{}/factors/{}/verify'.format(user_id, factor_id), data=serialize({'passCode': passcode}))

        self._api_client.check_api_response(response, status_code)

"""Wrapper for OKTA authentication calls"""
from theocktany.decorators import verify_user_id, verify_user_phone_number
from theocktany.exceptions import EnrollmentException
from theocktany.serializers import serialize


class OktaAuthClient(object):
    """Client for interacting with OKTA's authentication system

    :param api_client: the base API client
    :type api_client: theocktany.ApiClient
    """

    def __init__(self, api_client):
        self._api_client = api_client

    def _get_factor_id(self, user_id, factor_type="sms"):
        """Get the OKTA MFA factor ID

        :param user_id: OKTA id of the user
        :type user_id: str
        :param factor_type: name of the OKTA factor type
        :type factor_type: str
        :return: the factor id as a string
        :raises: ApiException, EnrollmentException
        """

        response, status_code = self._api_client.get('/api/v1/users/{}/factors'.format(user_id))

        self._api_client.check_api_response(response, status_code)

        for factor in response:
            if factor['factorType'] == factor_type:
                return factor['id']
        else:
            raise EnrollmentException("User not associated with sms factor")

    @verify_user_id
    @verify_user_phone_number
    def enroll_user_for_sms(self, user):
        """Begin user enrollment process for SMS multi-factor authentication.

        :param user: user object
        :type user: theocktany.User
        :raises: ValueError, ApiException

        """

        data = {
            "factorType": "sms",
            "provider": "OKTA",
            "profile": {
                "phoneNumber": user.phone_number
            }
        }
        response, status_code = self._api_client.post(
            '/api/v1/users/{}/factors'.format(user.id), data=serialize(data))

        self._api_client.check_api_response(response, status_code)

    @verify_user_id
    def activate_sms_factor(self, user, passcode):
        """Activate the SMS authentication factor for a user.

        :param user: user object
        :type user: theocktany.User
        :param passcode: the SMS passcode received by the user
        :type passcode: str
        :raises: ValueError, ApiException
        """

        factor_id = self._get_factor_id(user.id, 'sms')

        response, status_code = self._api_client.post(
            '/api/v1/users/{}/factors/{}/lifecycle/activate'.format(user.id, factor_id),
            data=serialize({'passCode': passcode}))

        self._api_client.check_api_response(response, status_code)

    @verify_user_id
    def send_sms_challenge(self, user):
        """Send the SMS challenge to the user enrolled in SMS MFA.

        :param user: user object
        :type user: theocktany.User
        :raises: ValueError, ApiException
        """

        factor_id = self._get_factor_id(user.id, 'sms')

        response, status_code = self._api_client.post('/api/v1/users/{}/factors/{}/verify'.format(user.id, factor_id))

        self._api_client.check_api_response(response, status_code)

    @verify_user_id
    def verify_sms_challenge_passcode(self, user, passcode):
        """Verify that the user received the correct passcode.

        :param user: user object
        :type user: theocktany.User
        :param passcode: the SMS passcode received by the user
        :type passcode: str
        :raises: ValueError, ApiException
        """

        factor_id = self._get_factor_id(user.id, 'sms')

        response, status_code = self._api_client.post(
            '/api/v1/users/{}/factors/{}/verify'.format(user.id, factor_id), data=serialize({'passCode': passcode}))

        self._api_client.check_api_response(response, status_code)

"""Wrapper for OKTA authentication calls"""
from theocktany.exceptions import ApiException,EnrollmentException
from theocktany.serializers import serialize


class OktaAuthClient(object):

    def __init__(self, api_client):
        self._api_client = api_client

    def _get_factor_id(self, user_id, factor_type="sms"):
        response, status_code = self._api_client.get('/api/v1/users/{}/factors'.format(user_id))

        if status_code != 200:
            if response['errorCauses']:
                msg = response['errorCauses'][0]['errorSummary']
            else:
                msg = response['errorSummary']
            raise ApiException(msg)

        for factor in response:
            if factor['factorType'] == factor_type:
                return factor['id']
        else:
            raise EnrollmentException("User not associated with sms factor")

    def _check_api_response(self, response, status_code):

        if status_code != 200:
            if 'errorCauses' in response:
                if response['errorCauses']:
                    msg = response['errorCauses'][0]['errorSummary']
                else:
                    msg = response['errorSummary']
            else:
                msg = 'Okta returned {}.'.format(status_code)
            raise ApiException(msg)

    def enroll_user_for_sms(self, user):
        """Enroll a user in SMS two factor authentication"""

        if not (user.id and user.phone_number):
            raise ValueError('User must have an OKTA id and phone number')

        data = {
            "factorType": "sms",
            "provider": "OKTA",
            "profile": {
                "phoneNumber": user.phone_number
            }
        }
        response, status_code = self._api_client.post(
            '/api/v1/users/{}/factors'.format(user.id), data=serialize(data))

        self._check_api_response(response, status_code)

    def activate_sms_factor(self, user, passcode):
        """Activate the SMS factor for an user"""

        if not user.id:
            raise ValueError('User must have an OKTA id.')

        factor_id = self._get_factor_id(user.id, 'sms')

        response, status_code = self._api_client.post(
            '/api/v1/users/{}/factors/{}/lifecycle/activate'.format(user.id, factor_id),
            data=serialize({'passCode': passcode}))

        self._check_api_response(response, status_code)

    def send_sms_challenge(self, user):
        """Sending the SMS challenge to the user enrolled for SMS factor"""

        if not user.id:
            raise ValueError('User must have an OKTA id.')

        factor_id = self._get_factor_id(user.id, 'sms')

        response, status_code = self._api_client.post('/api/v1/users/{}/factors/{}/verify'.format(user.id, factor_id))

        self._check_api_response(response, status_code)

    def verify_sms_challenge_passcode(self, user, passcode):

        if not user.id:
            raise ValueError('User must have an OKTA id.')

        factor_id = self._get_factor_id(user.id, 'sms')

        response, status_code = self._api_client.post(
            '/api/v1/users/{}/factors/{}/verify'.format(user.id, factor_id), data=serialize({'passCode': passcode}))

        self._check_api_response(response, status_code)

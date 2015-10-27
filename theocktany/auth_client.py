"""Wrapper for OKTA authentication calls"""
from theocktany.exceptions import ApiException,EnrollmentException
from theocktany.serializers import serialize


class OktaAuthClient(object):

    def __init__(self, api_client):
        self._api_client = api_client

    def enroll_user_for_sms(self, user):
        """Enroll a user in SMS two factor authentication"""

        if not (user.id and user.phone_number):
            raise ValueError('User must have an OKTA id and phone number')

        response, status_code = self._api_client.post(
            '/api/v1/users/{}/factors'.format(user.id), data=serialize({'test': 'test'}))

        if status_code != 200:
            if response['errorCauses']:
                msg = response['errorCauses'][0]['errorSummary']
            else:
                msg = response['errorSummary']
            raise ApiException(msg)

    def activate_sms_factor(self, user, passcode):
        """Activate the SMS factor for an user"""

        if not (user.id and user.phone_number):
            raise ValueError('User must have an OKTA id and phone number')

        # Get the factor id
        response, status_code = self._api_client.get('/api/v1/users/{}/factors'.format(user.id))

        if status_code != 200:
            if response['errorCauses']:
                msg = response['errorCauses'][0]['errorSummary']
            else:
                msg = response['errorSummary']
            raise ApiException(msg)

        for factor in response:
            if factor['factorType'] == 'sms':
                factor_id = factor['id']
                break
        else:
            raise EnrollmentException("User not associated with sms factor")

        response, status_code = self._api_client.post(
            '/api/v1/users/{}/factors/{}/lifecycle/activate'.format(user.id, factor_id),
            data=serialize({'passCode': passcode}))

        if status_code != 200:
            if response['errorCauses']:
                msg = response['errorCauses'][0]['errorSummary']
            else:
                msg = response['errorSummary']
            raise ApiException(msg)

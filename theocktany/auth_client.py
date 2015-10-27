"""Wrapper for OKTA authentication calls"""
from theocktany.exceptions import ApiException
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
            raise ApiException(msg=msg)

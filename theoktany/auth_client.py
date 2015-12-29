import requests

from theoktany.serializers import serialize
from theoktany.client import ApiClient


def _validate(response, status_code):
    if status_code in [200, 201, 202, 204]:
        return response, "Success", None

    error_code = response.get('errorCode')

    try:
        if response.get('errorCauses'):
            message = response['errorCauses'][0]['errorSummary']
        elif response.get('errorSummary'):
            message = response['errorSummary']
        else:
            message = 'Okta returned {}.'.format(status_code)
    except KeyError:
        message = 'Okta returned {}.'.format(status_code)

    return False, message, error_code


def _get_shared_secret_from_response(response):
    if '_embedded' in response and 'activation' in response['_embedded']:
        try:
            return response['_embedded']['activation']['sharedSecret']
        except KeyError:
            pass
    return None


def _get_qr_code_from_response(response):
    if '_embedded' in response and 'activation' in response['_embedded']:
        try:
            qr_response = requests.get(response['_embedded']['activation']['_links']['qrcode']['href'], stream=True)
            return qr_response.raw
        except (KeyError, requests.RequestException):
            pass
    return None


class OktaFactors(object):
    def __init__(self, api_client=ApiClient):
        self._api_client = api_client

    def get_factors(self, user_id):
        # noinspection PyArgumentList
        return _validate(*self._api_client.get('/api/v1/users/{}/factors'.format(user_id)))

    @staticmethod
    def filter_by_type(factors, factor_type='sms', provider='OKTA'):
        return [factor for factor in factors if factor['factorType'] == factor_type and factor['provider'] == provider]

    @staticmethod
    def create_factor_object(factor_type, provider, phone_number=None):
        factor = {
            "factorType": factor_type,
            "provider": provider,
        }

        if phone_number:
            factor["profile"] = {"phoneNumber": phone_number}

        return factor

    def is_enrolled(self, user_id, factor_type, provider):
        factors, message, error_code = self.get_factors(user_id)
        if factors and not error_code:
            filtered_factors = self.filter_by_type(factors, factor_type, provider)
            if filtered_factors and filtered_factors[0]['status'] == 'ACTIVE':
                return True
        return False

    def call_with_correct_factor(self, v, user_id, factor_type, provider):
        factors, message, error_code = self.get_factors(user_id)
        if factors and not error_code:
            filtered_factors = self.filter_by_type(factors, factor_type, provider)

            if filtered_factors:
                factor_id = filtered_factors[0]['id']
                return v(factor_id)
            else:
                return False, "Not enrolled for SMS.", '1'

        return False, message, error_code

    def enroll(self, user_id, phone_number=None, factor_type='sms', provider='OKTA'):
        assert user_id
        assert (phone_number and factor_type == 'sms') or (not phone_number and factor_type != 'sms')
        assert factor_type
        assert provider

        data = self.create_factor_object(provider=provider, factor_type=factor_type, phone_number=phone_number)
        route = '/api/v1/users/{}/factors'.format(user_id)

        if factor_type == 'sms':
            route += '?updatePhone=true'

        # noinspection PyArgumentList
        response, status_code = self._api_client.post(route, data=serialize(data))
        result = _validate(response, status_code)

        if 'totp' in factor_type:
            result = (*result, {})
            if result[0]:   # result[0] is success
                result[-1]['shared_secret'] = _get_shared_secret_from_response(response)
                result[-1]['qr_code'] = _get_qr_code_from_response(response)

        return result

    def activate(self, user_id, passcode, factor_type='sms', provider='OKTA'):
        assert user_id
        assert passcode

        def v(factor_id):
            route = '/api/v1/users/{}/factors/{}/lifecycle/activate'.format(user_id, factor_id)
            # noinspection PyArgumentList
            return _validate(*self._api_client.post(route, data=serialize({'passCode': passcode})))

        return self.call_with_correct_factor(v, user_id, factor_type, provider)

    def delete(self, user_id, factor_type='sms', provider='OKTA'):
        assert user_id

        def v(factor_id):
            route = '/api/v1/users/{}/factors/{}'.format(user_id, factor_id)
            # noinspection PyArgumentList
            return _validate(*self._api_client.delete(route))

        return self.call_with_correct_factor(v, user_id, factor_type, provider)

    def challenge(self, user_id, factor_type='sms', provider='OKTA'):
        assert user_id

        def v(factor_id):
            route = '/api/v1/users/{}/factors/{}/verify'.format(user_id, factor_id)
            # noinspection PyArgumentList
            return _validate(*self._api_client.post(route))

        return self.call_with_correct_factor(v, user_id, factor_type, provider)

    def verify(self, user_id, passcode, factor_type='sms', provider='OKTA'):
        assert user_id
        assert passcode

        def v(factor_id):
            route = '/api/v1/users/{}/factors/{}/verify'.format(user_id, factor_id)
            # noinspection PyArgumentList
            return _validate(*self._api_client.post(route, data=serialize({'passCode': passcode})))

        return self.call_with_correct_factor(v, user_id, factor_type, provider)


class OktaAuthClient(object):

    def __init__(self, factors):
        self.factors = factors

    def enroll_user_for_sms(self, user_id, phone_number):
        return self.factors.enroll(user_id, phone_number)

    def activate_sms_factor(self, user_id, passcode):
        return self.factors.activate(user_id, passcode)

    def send_sms_challenge(self, user_id):
        return self.factors.challenge(user_id)

    def verify_sms_challenge_passcode(self, user_id, passcode):
        return self.factors.verify(user_id, passcode)

    def is_user_enrolled_for_sms(self, user_id):
        return self.factors.is_enrolled(user_id, factor_type='sms', provider='OKTA')

    def delete_sms_factor(self, user_id):
        return self.factors.delete(user_id, factor_type="sms")

    def update_sms_phone_number(self, user_id, phone_number):
        success, message, error_code = self.delete_sms_factor(user_id)
        if message != 'Success':
            return success, message, error_code
        return self.enroll_user_for_sms(user_id, phone_number)

    def enroll_user_for_google_authenticator(self, user_id):
        return self.factors.enroll(user_id, factor_type='token:software:totp', provider='GOOGLE')

    def activate_google_authenticator_factor(self, user_id, passcode):
        return self.factors.activate(user_id, passcode, factor_type='token:software:totp', provider='GOOGLE')

    def verify_google_authenticator_factor(self, user_id, passcode):
        return self.factors.verify(user_id, passcode, factor_type='token:software:totp', provider='GOOGLE')

    def is_user_enrolled_for_google_authenticator(self, user_id):
        return self.factors.is_enrolled(user_id, factor_type='token:software:totp', provider='GOOGLE')

    def delete_google_authenticator_factor(self, user_id):
        return self.factors.delete(user_id, factor_type='token:software:totp', provider='GOOGLE')

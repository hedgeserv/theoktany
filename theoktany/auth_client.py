from theoktany.serializers import serialize
from theoktany.client import ApiClient


def _validate(response, status_code):
    if status_code in [200, 201, 202, 204]:
        return response, "Success", None

    if response.get('errorCode'):
        error_code = response['errorCode']
    else:
        error_code = None

    if response.get('errorCauses'):
        message = response['errorCauses'][0]['errorSummary']
    elif response.get('errorSummary'):
        message = response['errorSummary']
    else:
        message = 'Okta returned {}.'.format(status_code)

    return False, message, error_code


class OktaFactors(object):
    def __init__(self, api_client=ApiClient):
        self._api_client = api_client

    def get_factors(self, user_id):
        # noinspection PyArgumentList
        return _validate(*self._api_client.get('/api/v1/users/{}/factors'.format(user_id)))

    @staticmethod
    def filter_by_type(factors, factor_type="sms"):
        return [factor for factor in factors if factor['factorType'] == factor_type]

    @staticmethod
    def create_factor_object(phone_number, factor_type="sms"):
        return {
            "factorType": factor_type,
            "provider": "OKTA",
            "profile": {
                "phoneNumber": phone_number
            }
        }

    def is_enrolled(self, user_id, factor_type):
        factors, message, error_code = self.get_factors(user_id)
        if factors and not error_code:
            filtered_factors = self.filter_by_type(factors, factor_type)
            if filtered_factors and filtered_factors[0]['status'] == 'ACTIVE':
                return True
        return False

    def call_with_correct_factor(self, v, user_id, factor_type):
        factors, message, error_code = self.get_factors(user_id)
        if factors and not error_code:
            filtered_factors = self.filter_by_type(factors, factor_type)

            if filtered_factors:
                factor_id = filtered_factors[0]['id']
                return v(factor_id)
            else:
                return False, "Not enrolled for SMS.", '1'

        return False, message, error_code

    def enroll(self, user_id, phone_number, factor_type="sms"):
        assert user_id
        assert phone_number

        data = self.create_factor_object(phone_number, factor_type)
        route = '/api/v1/users/{}/factors'.format(user_id)

        if factor_type == "sms":
            route += '?updatePhone=true'

        # noinspection PyArgumentList
        return _validate(*self._api_client.post(route, data=serialize(data)))

    def activate(self, user_id, pass_code, factor_type="sms"):
        assert user_id
        assert pass_code

        def v(factor_id):
            route = '/api/v1/users/{}/factors/{}/lifecycle/activate'.format(user_id, factor_id)
            # noinspection PyArgumentList
            return _validate(*self._api_client.post(route, data=serialize({'passCode': pass_code})))

        return self.call_with_correct_factor(v, user_id, factor_type)

    def delete(self, user_id, factor_type="sms"):
        assert user_id

        def v(factor_id):
            route = '/api/v1/users/{}/factors/{}'.format(user_id, factor_id)
            # noinspection PyArgumentList
            return _validate(*self._api_client.delete(route))

        return self.call_with_correct_factor(v, user_id, factor_type)

    def challenge(self, user_id, factor_type="sms"):
        assert user_id

        def v(factor_id):
            route = '/api/v1/users/{}/factors/{}/verify'.format(user_id, factor_id)
            # noinspection PyArgumentList
            return _validate(*self._api_client.post(route))

        return self.call_with_correct_factor(v, user_id, factor_type)

    def verify(self, user_id, pass_code, factor_type="sms"):
        assert user_id
        assert pass_code

        def v(factor_id):
            route = '/api/v1/users/{}/factors/{}/verify'.format(user_id, factor_id)
            # noinspection PyArgumentList
            return _validate(*self._api_client.post(route, data=serialize({'passCode': pass_code})))

        return self.call_with_correct_factor(v, user_id, factor_type)


class OktaAuthClient(object):

    def __init__(self, factors):
        self.factors = factors

    def enroll_user_for_sms(self, user_id, phone_number):
        return self.factors.enroll(user_id, phone_number)

    def activate_sms_factor(self, user_id, pass_code):
        return self.factors.activate(user_id, pass_code)

    def send_sms_challenge(self, user_id):
        return self.factors.challenge(user_id)

    def verify_sms_challenge_passcode(self, user_id, pass_code):
        return self.factors.verify(user_id, pass_code)

    def is_user_enrolled_for_sms(self, user_id):
        return self.factors.is_enrolled(user_id, factor_type="sms")

    def delete_sms_factor(self, user_id):
        return self.factors.delete(user_id, factor_type="sms")

    def update_sms_phone_number(self, user_id, phone_number):
        success, message, error_code = self.delete_sms_factor(user_id)
        if message != 'Success':
            return success, message, error_code
        return self.enroll_user_for_sms(user_id, phone_number)

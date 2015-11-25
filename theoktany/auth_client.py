from theoktany.serializers import serialize
from theoktany.validate import validate
from theoktany.client import ApiClient

class OktaFactors(object):
    def __init__(self, api_client=ApiClient):
        self._api_client = api_client

    def get_factors(self, user_id):
        return validate(*self._api_client.get('/api/v1/users/{}/factors'.format(user_id)))

    def filter_by_type(self, factors, factor_type="sms"):
        return [factor for factor in factors if factor['factorType'] == factor_type]

    def create_factor_object(self, phone_number, factor_type="sms"):
        return {
            "factorType": factor_type,
            "provider": "OKTA",
            "profile": {
                "phoneNumber": phone_number
            }
        }

    def is_enrolled(self, user_id, factor_type):
        factors, message = self.get_factors(user_id)
        if factors:
            filtered_factors = self.filter_by_type(factors, factor_type)
            if filtered_factors and filtered_factors[0]['status'] == 'ACTIVE':
                return True
        return False

    def call_with_correct_factor(self, v, user_id, factor_type):
        factors, message = self.get_factors(user_id)
        if factors:
            filtered_factors = self.filter_by_type(factors, factor_type)

            if filtered_factors:
                factor_id = filtered_factors[0]['id']
                return v(factor_id)
            else:
                return False, "Not enrolled for SMS."

        return False, message

    def enroll(self, user_id, phone_number, factor_type="sms"):
        assert user_id
        assert phone_number

        data = self.create_factor_object(phone_number, factor_type)
        route = '/api/v1/users/{}/factors'.format(user_id)
        return validate(*self._api_client.post(route, data=serialize(data)))

    def activate(self, user_id, pass_code, factor_type="sms"):
        assert user_id
        assert pass_code

        def v(factor_id):
            route = '/api/v1/users/{}/factors/{}/lifecycle/activate'.format(user_id, factor_id)
            return validate(*self._api_client.post(route, data=serialize({'passCode': pass_code})))

        return self.call_with_correct_factor(v, user_id, factor_type)

    def challenge(self, user_id, factor_type="sms"):
        assert user_id

        def v(factor_id):
            route = '/api/v1/users/{}/factors/{}/verify'.format(user_id, factor_id)
            return validate(*self._api_client.post(route))

        return self.call_with_correct_factor(v, user_id, factor_type)

    def verify(self, user_id, pass_code, factor_type="sms"):
        assert user_id
        assert pass_code

        def v(factor_id):
            route = '/api/v1/users/{}/factors/{}/verify'.format(user_id, factor_id)
            return validate(*self._api_client.post(route, data=serialize({'passCode': pass_code})))

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

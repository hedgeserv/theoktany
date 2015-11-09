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

    def create_factor_object(self, user, factor_type="sms"):
        return {
            "factorType": factor_type,
            "provider": "OKTA",
            "profile": {
                "phoneNumber": user.get('phone_number')
            }
        }

    def call_with_correct_factor(self, v, user, factor_type):
        factors, message = self.get_factors(user.get('id'))
        if factors:
            filtered_factors = self.filter_by_type(factors, factor_type)

            if filtered_factors:
                factor_id = filtered_factors[0]['id']
                return v(factor_id)
            else:
                return False, "Not enrolled for SMS."

        return False, message

    def enroll(self, user, factor_type="sms"):
        assert user.get('id')
        assert user.get('phone_number')

        data = self.create_factor_object(user, factor_type)
        route = '/api/v1/users/{}/factors'.format(user.get('id'))
        return validate(*self._api_client.post(route, data=serialize(data)))

    def activate(self, user, pass_code, factor_type="sms"):
        assert user.get('id')
        assert pass_code

        def v(factor_id):
            route = '/api/v1/users/{}/factors/{}/lifecycle/activate'.format(user.get('id'), factor_id)
            return validate(*self._api_client.post(route, data=serialize({'passCode': pass_code})))

        return self.call_with_correct_factor(v, user, factor_type)

    def challenge(self, user, factor_type="sms"):
        assert user.get('id')

        def v(factor_id):
            route = '/api/v1/users/{}/factors/{}/verify'.format(user.get('id'), factor_id)
            return validate(*self._api_client.post(route))

        return self.call_with_correct_factor(v, user, factor_type)

    def verify(self, user, pass_code, factor_type="sms"):
        assert user.get('id')
        assert pass_code

        def v(factor_id):
            route = '/api/v1/users/{}/factors/{}/verify'.format(user.get('id'), factor_id)
            return validate(*self._api_client.post(route, data=serialize({'passCode': pass_code})))

        return self.call_with_correct_factor(v, user, factor_type)


class OktaAuthClient(object):

    def __init__(self, factors):
        self.factors = factors

    def enroll_user_for_sms(self, user_id, phone_number):
        return self.factors.enroll(self.create_user_object(user_id, phone_number))

    def activate_sms_factor(self, user_id, phone_number, pass_code):
        return self.factors.activate(self.create_user_object(user_id, phone_number), pass_code)

    def send_sms_challenge(self, user_id, phone_number):
        return self.factors.challenge(self.create_user_object(user_id, phone_number))

    def verify_sms_challenge_passcode(self, user_id, phone_number, pass_code):
        return self.factors.verify(self.create_user_object(user_id, phone_number), pass_code)

    def create_user_object(self, user_id, phone_number):
        return dict(id=user_id, phone_number=phone_number)
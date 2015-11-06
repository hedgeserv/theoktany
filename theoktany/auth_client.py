"""Wrapper for OKTA authentication calls"""
from theoktany.exceptions import ApiException,EnrollmentException
from theoktany.serializers import serialize
from theoktany import validate

class OktaFactors(object):
    def __init__(self, api_client, validate, **kwargs):
        self._api_client = api_client
        self.validate = validate

    def get(self, user_id):
        return validate(*self._api_client.get('/api/v1/users/{}/factors'.format(user_id)))

    def filter_by_type(self, factors, factor_type="sms"):
        return [factor for factor in factors if factor['factorType'] == factor_type]

    def enroll(self, user, factor_type="sms"):
        assert user.id
        assert user.phone_number

        data = {
            "factorType": "sms",
            "provider": "OKTA",
            "profile": {
                "phoneNumber": user.phone_number
            }
        }

        return validate(*self._api_client.post(
            '/api/v1/users/{}/factors'.format(user.id), data=serialize(data)))

    def call_with_correct_factor(self, v, user, factor_type):
        factors, err = self.get(user.id)
        if factors:
            filtered_factors = self.filter_by_type(factors, factor_type)

            if(filtered_factors):
                factor_id = filtered_factors[0]['id']
                return v(factor_id)

        return False, "Not Enrolled for SMS " + err

    def activate(self, user, passcode, factor_type="sms"):
        assert user.id
        assert passcode

        def v(factor_id):
            validate(*self._api_client.post(
                '/api/v1/users/{}/factors/{}/lifecycle/activate'.format(user.id, factor_id),
                data=serialize({'passCode': passcode})))

        return self.call_with_correct_factor(v, user, factor_type)

    def challenge(self, user, factor_type="sms"):
        assert user.id

        def v(factor_id):
            return validate(*self._api_client.post('/api/v1/users/{}/factors/{}/verify'.
                                              format(user.id, factor_id)))
        return self.call_with_correct_factor(v, user, factor_type)

    def verify(self, user, passcode, factor_type="sms"):
        assert user.id
        assert passcode

        def v(factor_id):
            validate(*self._api_client.post('/api/v1/users/{}/factors/{}/verify'.
                     format(user.id, factor_id), data=serialize({'passCode': passcode})))

        return self.call_with_correct_factor(v, user, factor_type)


class OktaAuthClient(object):

    def __init__(self, factors):
        self.factors = factors

    def enroll_user_for_sms(self, user):
        self.factors.enroll(user)

    def activate_sms_factor(self, user, passcode):
        self.factors.activate(user, passcode)

    def send_sms_challenge(self, user):
        self.factors.challenge(user)

    def verify_sms_challenge_passcode(self, user, passcode):
        self.factors.verify(user, passcode)

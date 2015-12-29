import json


class UserBroker:
    def __init__(self, api_client):
        self._api_client = api_client
        self.route = '/api/v1/users'

    @staticmethod
    def _format_user_data_to_send(user_data):

        user_dict = {
            "id": user_data.get('id', 'None'),
            "profile": {}
        }
        if 'mobile_phone' in user_data:
            user_dict['profile']['mobilePhone'] = user_data['mobile_phone']
        if 'first_name' in user_data:
            user_dict['profile']['firstName'] = user_data['first_name']
        if 'last_name' in user_data:
            user_dict['profile']['lastName'] = user_data['last_name']
        if 'email' in user_data:
            user_dict['profile']['email'] = user_data['email']
            user_dict['profile']['login'] = user_data['email']
        if 'login' in user_data:
            user_dict['profile']['login'] = user_data['login']

        return json.dumps(user_dict)

    @staticmethod
    def _format_user_data_received(user_data):
        user_dict = {
            'id': user_data['id'],
            'login': user_data['profile']['login'],
            'email': user_data['profile']['email'],
            'mobile_phone': user_data['profile']['mobilePhone'],
            'factors': [],
        }
        return user_dict

    @staticmethod
    def _format_user_factors_received(factors_data):
        factors = []

        for factor in factors_data:
            factors.append({
                'id': factor['id'],
                'type': factor['factorType'],
                'phone_number': factor['profile']['phoneNumber']
            })

        return factors

    @staticmethod
    def _validate_user_data(user):
        fields = ['mobile_phone', 'first_name', 'last_name', 'email']
        if not all([field in user and user[field] for field in fields]):
            raise AssertionError(
                'Dictionary is missing some fields - it must have mobile_phone, first_name, last_name, and email.')

    def _create_update_user_path(self, user_id):
        return self.route + "/" + user_id

    def create_user(self, user_data):
        self._validate_user_data(user_data)
        user = self._format_user_data_to_send(user_data)
        route = self.route
        response, status_code = self._api_client.post(route, user)

        if len(response) and status_code in [200, 201]:
            return self._format_user_data_received(response)

    def get_user_id(self, email):
        user = self.get_user(email)
        if user:
            return user['id']

    def get_user(self, email):
        filter_string = 'filter=profile.login+eq+"%s"&limit=1' % email
        route = self.route + '?' + filter_string

        # first, get the user data
        user_response, status_code = self._api_client.get(route)
        if not (len(user_response) and status_code == 200 and 'id' in user_response[0]):
            return None

        user_data = self._format_user_data_received(user_response[0])

        # now, get all the factors
        factor_route = self._create_update_user_path(user_data['id']) + '/factors'
        factors_response, status_code = self._api_client.get(factor_route)
        if not status_code == 200:
            return None
        user_data['factors'] = self._format_user_factors_received(factors_response)

        return user_data

    def update_user_phone_number(self, user_id, phone_number):
        assert user_id
        assert phone_number

        user = self._format_user_data_to_send({'id': user_id, 'mobile_phone': phone_number})
        route = self._create_update_user_path(user_id)
        response, status_code = self._api_client.post(route, user)

        if len(response) and status_code == 200:
            return self._format_user_data_received(response)

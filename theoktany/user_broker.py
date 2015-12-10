import json

from theoktany.auth_client import OktaAuthClient, OktaFactors


class UserBroker:
    def __init__(self, api_client, auth_client=None, factors=None):
        self._api_client = api_client
        self._auth_client = auth_client or OktaAuthClient(factors or OktaFactors(api_client))
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
            user_dict['profile']['login'] = user_data['email']
            user_dict['profile']['email'] = user_data['email']

        return json.dumps(user_dict)

    @staticmethod
    def _format_user_data_received(user_data):
        user_dict = {
            'id': user_data['id'],
            'login': user_data['profile']['login'],
            'mobile_phone': user_data['profile']['mobilePhone']
        }
        return user_dict

    @staticmethod
    def _validate_user_data(user):
        fields = ['mobile_phone', 'first_name', 'last_name', 'email']
        if not all([field in user and user[field] for field in fields]):
            raise AssertionError(
                'Dictionary is missing some fields - it must have mobile_phone, first_name, last_name, and email.')

    def create_user(self, user_data):
        self._validate_user_data(user_data)
        user = self._format_user_data_to_send(user_data)
        route = self.route
        response, status_code = self._api_client.post(route, user)
        return response, status_code

    def get_user_id(self, email):
        user = self.get_user(email)
        if user:
            return user['id']

    def get_user(self, email):
        filter_string = 'filter=profile.login+eq+"%s"&limit=1' % email
        route = self.route + '?' + filter_string

        response, status_code = self._api_client.get(route)

        if len(response) and status_code == 200:
            return self._format_user_data_received(response[0])

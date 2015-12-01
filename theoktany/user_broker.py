import json


class UserBroker:
    def __init__(self, api_client):
        self._api_client = api_client
        self.route = '/api/v1/users'

    def format_user_data_to_send(self, user_data):

        user_dict = {
            "id": user_data.pop('id', 'None'),
            "profile": {}
        }
        for key, val in user_data.items():
            user_dict['profile'][key] = val

        return json.dumps(user_dict)

    def create_update_user_path(self, user_id):
        return self.route + "/" + user_id

    def create_user(self, user_data):
        self.validate_user_data(user_data)
        user = self.format_user_data_to_send(user_data)
        route = self.route
        response, status_code = self._api_client.post(route, user)
        return response, status_code

    def get_user_id(self, user_login):
        user = self.get_user(user_login)
        if user:
            return user['id']

    def get_user(self, user_login):
        filter_string = "filter=profile.login+eq+\"" + user_login + "\"" + '&limit=1'
        route = self.route + '?' + filter_string

        response, status_code = self._api_client.get(route)

        if len(response) and status_code == 200:
            return response[0]

    def update_user_phone_number(self, user_id, phone_number):
        assert user_id
        assert phone_number

        user = self.format_user_data_to_send({'id': user_id, 'mobilePhone': phone_number})
        route = self.create_update_user_path(user_id)
        response, status_code = self._api_client.post(route, user)
        return response, status_code

    def validate_user_data(self, user):
        fields = ['login', 'mobilePhone', 'firstName', 'lastName', 'email']
        if not all([field in user and user[field] for field in fields]):
            raise AssertionError('user is missing fields')

import json


class UserBroker:
    def __init__(self, api_client):
        self._api_client = api_client
        self.route = '/api/v1/users'

    def format_user_data_to_send(self, user_data):
        return json.dumps({
            "id": user_data.get('id') or "None",
            "profile": {
                "login": user_data.get('login'),
                "mobilePhone": user_data.get('mobilePhone'),
                "firstName": user_data.get('firstName'),
                "lastName": user_data.get('lastName'),
                "email": user_data.get('email')
            }
        })

    def create_update_user_path(self, user_id):
        return self.route + "/" + user_id

    def create_user(self, user_data):
        user = self.format_user_data_to_send(user_data)
        route = self.route
        response, status_code = self._api_client.post(route, user)
        return response, status_code

    def get_user_id(self, user_login):
        filter_string = "filter=profile.login+eq+\"" + user_login + "\"" + '&limit=1'
        route = self.route + '?' + filter_string

        response, status_code = self._api_client.get(route)

        if not len(response) or not status_code == 200:
            return None
        return response[0]['id']

    def invalid_user_data(self):
        return 'Invalid user data'  # Need to handle error response

    def update_user(self, user_data):
        user = self.format_user_data_to_send(user_data)
        route = self.create_update_user_path(user_data.get('id'))
        response, status_code = self._api_client.post(route, user)
        return response, status_code

    def upsert_user(self, user_data):
        if not self.validate_user_data(user_data):
            return self.invalid_user_data()

        user = self.user_exists(user_data)

        if user.get('id'):
            return self.update_user(user)
        return self.create_user(user_data)

    def user_exists(self, user_data):
        if user_data.get('id'):
            return user_data

        user_data['id'] = self.get_user_id(user_data.get('login'))
        return user_data

    def validate_user_data(self, user):
        fields = ['login', 'mobilePhone', 'firstName', 'lastName', 'email']
        for field in fields:
            if not user.get(field):
                return False
        return True

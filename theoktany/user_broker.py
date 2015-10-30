class UserBroker:
    def __init__(self, api_client):
        self._api_client = api_client
        self.route = '/api/v1/users'

    def create_profile_object_from_user_data(self, user_data):
        return {
            "profile": user_data['profile']
        }

    def create_get_user_path(self, user_login):
        filter_string = "filter=profile.login+eq+\"" + user_login + "\""
        limit_string = 'limit=1'
        return self.route + '?' + filter_string + '&' + limit_string

    def create_update_user_path(self, user_id):
        return self.route + "/" + user_id

    def create_user(self, user_data):
        user = self.create_profile_object_from_user_data(user_data)
        route = self.route
        response, status_code = self._api_client.post(route, user)

        return response, status_code

    def get_user(self, route, user_data):
        response, status_code = self._api_client.get(route)

        if not len(response) or not status_code == 200:
            return None

        user = response[0]
        user_data['id'] = user['id']

        return user_data

    def invalid_user_data(self):
        return 'Invalid user data'  # Need to handle error response

    def update_user(self, user_data):
        user = self.create_profile_object_from_user_data(user_data)
        route = self.create_update_user_path(user_data.get('id'))
        response, status_code = self._api_client.post(route, user)

        return response, status_code

    def upsert_user(self, user_data):
        if not self.validate_user_data(user_data):
            return self.invalid_user_data()

        user = self.user_exists(user_data)

        if user:
            return self.update_user(user)
        return self.create_user(user_data)

    def user_exists(self, user_data):
        if user_data.get('id'):
            return user_data

        login = user_data['profile']['login']
        route = self.create_get_user_path(login)

        return self.get_user(route, user_data)

    def validate_user_data(self, user_data):
        try:
            profile = user_data['profile']
            first = profile['firstName']
            last = profile['lastName']
            email = profile['email']
            login = profile['login']
            phone = profile['mobilePhone']
            if first and last and email and login and phone:
                return True
        except KeyError:
            return False

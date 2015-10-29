import unittest
from theocktany.user_broker import UserBroker
from theocktany.client import ApiClient

from tests.mb_wrapper import MountebankProcess

MOUNTEBANK_URL = "localhost:2525"

existing_user = {
    "id": "00001",
    "profile": {
        "firstName": "Dave",
        "lastName": "Davidson",
        "email": "dave@aol.com",
        "login": "dave@aol.com",
        "mobilePhone": "123-456-7890"
    }
}

new_user_with_phone_number = {
    "id": None,
    "profile": {
        "firstName": "Gary",
        "lastName": "Garrison",
        "email": "gary@aol.com",
        "login": "gary@aol.com",
        "mobilePhone": "234-567-8901"
    }
}

new_user_without_phone_number = {
    "id": None,
    "profile": {
        "firstName": "Maury",
        "lastName": "Morrison",
        "email": "maury@aol.com",
        "login": "maury@aol.com",
        "mobilePhone": None
    }
}


class TestUserBroker(unittest.TestCase):
    def setUp(self):
        self.mb = MountebankProcess()

        imposter = self.mb.create_imposter('test_user_broker/stubs/test_create_or_update_user_with_valid_credentials.json')
        api_client = ApiClient(BASE_URL=self.mb.get_imposter_url(imposter))

        self.broker = UserBroker(api_client)

    def tearDown(self):
        self.mb.destroy_all_imposters()

    def test_create_new_user_with_invalid_credentials(self):
        response = self.broker.upsert_user(new_user_without_phone_number)
        self.assertEqual(response, 'Invalid user data')

    def test_create_new_user_with_valid_credentials(self):
        user, status_code = self.broker.upsert_user(new_user_with_phone_number)

        self.assertEqual(user['profile']['firstName'], new_user_with_phone_number['profile']['firstName'])
        self.assertEqual(user['id'], "00002")
        self.assertEqual(status_code, 200)

    def test_update_existing_user(self):
        user, status_code = self.broker.upsert_user(existing_user)

        self.assertEqual(user['profile']['firstName'], existing_user['profile']['firstName'])
        self.assertEqual(user['id'], existing_user['id'])
        self.assertEqual(status_code, 200)


if __name__ == '__main__':
    unittest.main()

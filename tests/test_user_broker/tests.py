import unittest

from theoktany.user_broker import UserBroker
from theoktany.client import ApiClient
from tests.mb_wrapper import MountebankProcess

MOUNTEBANK_URL = "localhost:2525"

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

existing_user_with_id = {
    "id": "00001",
    "profile": {
        "firstName": "Dave",
        "lastName": "Davidson",
        "email": "dave@aol.com",
        "login": "dave@aol.com",
        "mobilePhone": "123-456-7890"
    }
}

existing_user_without_id = {
    "id": None,
    "profile": {
        "firstName": "Harry",
        "lastName": "Harrison",
        "email": "harry@aol.com",
        "login": "harry@aol.com",
        "mobilePhone": "234-567-8901"
    }
}


class TestUserBroker(unittest.TestCase):
    def setUp(self):
        self.mb = MountebankProcess()
        api_client = ApiClient()
        self.broker = UserBroker(api_client)

    def tearDown(self):
        self.mb.destroy_all_imposters()

    def test_create_new_user_with_invalid_credentials(self):
        response = self.broker.upsert_user(new_user_without_phone_number)
        self.assertEqual(response, 'Invalid user data')

    def test_create_new_user_with_valid_credentials(self):
        self.setup_imposter('create_new_user.json')
        user, status_code = self.broker.upsert_user(new_user_with_phone_number)

        self.assertEqual(user['profile']['login'], new_user_with_phone_number['profile']['login'])
        self.assertEqual(user['id'], "00002")
        self.assertEqual(status_code, 200)

    def test_update_existing_user_with_id(self):
        self.setup_imposter('update_existing_user.json')
        user, status_code = self.broker.upsert_user(existing_user_with_id)

        self.assertEqual(user['profile']['login'], existing_user_with_id['profile']['login'])
        self.assertEqual(user['id'], existing_user_with_id['id'])
        self.assertEqual(status_code, 200)

    def test_update_existing_user_without_id(self):
        self.setup_imposter('update_existing_user.json')
        user, status_code = self.broker.upsert_user(existing_user_without_id)

        self.assertEqual(user['profile']['login'], existing_user_without_id['profile']['login'])
        self.assertEqual(user['id'], "00003")
        self.assertEqual(status_code, 200)

    def setup_imposter(self, file_name):
        file_path = 'test_user_broker/stubs/' + file_name
        imposter = self.mb.create_imposter(file_path)
        self.broker._api_client = ApiClient(BASE_URL=self.mb.get_imposter_url(imposter))

if __name__ == '__main__':
    unittest.main()

import unittest

from theoktany.user_broker import UserBroker
from theoktany.client import ApiClient
from tests.mb_wrapper import MountebankProcess

MOUNTEBANK_URL = "localhost:2525"

user_one = {
    "id": None,
    "login": "maury@aol.com",
    "phone": None
}

user_two = {
    "id": None,
    "login": "gary@aol.com",
    "phone": "234-567-8901"
}

user_three = {
    "id": "00001",
    "login": "dave@aol.com",
    "phone": "123-456-7890"
}

user_four = {
    "id": None,
    "login": "harry@aol.com",
    "phone": "345-6789-0123"
}


class TestUserBroker(unittest.TestCase):
    def setUp(self):
        self.mb = MountebankProcess()
        api_client = ApiClient()
        self.broker = UserBroker(api_client)

    def tearDown(self):
        self.mb.destroy_all_imposters()

    def test_create_new_user_with_invalid_data(self):
        response = self.broker.upsert_user(user_one.get('id'), user_one.get('login'), user_one.get('phone'))
        self.assertEqual(response, 'Invalid user data')

    def test_create_new_user_with_valid_data(self):
        self.setup_imposter('create_new_user.json')
        user, code = self.broker.upsert_user(user_two.get('id'), user_two.get('login'), user_two.get('phone'))
        self.assertEqual(code, 200)
        self.assertEqual(user['id'], "00002")
        self.assertEqual(user['profile']['login'], user_two.get('login'))
        self.assertEqual(user['profile']['mobilePhone'], user_two.get('phone'))

    def test_update_existing_user_with_id(self):
        self.setup_imposter('update_existing_user.json')
        user, code = self.broker.upsert_user(user_three.get('id'), user_three.get('login'), user_three.get('phone'))
        self.assertEqual(code, 200)
        self.assertEqual(user['id'], user_three.get('id'))
        self.assertEqual(user['profile']['login'], user_three.get('login'))
        self.assertEqual(user['profile']['mobilePhone'], user_three.get('phone'))

    def test_update_existing_user_without_id(self):
        self.setup_imposter('update_existing_user.json')
        user, code = self.broker.upsert_user(user_four.get('id'), user_four.get('login'), user_four.get('phone'))
        self.assertEqual(code, 200)
        self.assertEqual(user['id'], "00003")
        self.assertEqual(user['profile']['login'], user_four.get('login'))
        self.assertEqual(user['profile']['mobilePhone'], user_four.get('phone'))

    def setup_imposter(self, file_name):
        file_path = 'test_user_broker/stubs/' + file_name
        imposter = self.mb.create_imposter(file_path)
        self.broker._api_client = ApiClient(BASE_URL=self.mb.get_imposter_url(imposter))

if __name__ == '__main__':
    unittest.main()

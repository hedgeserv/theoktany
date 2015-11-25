import unittest

from theoktany.user_broker import UserBroker
from theoktany.client import ApiClient
from tests.mb_wrapper import MountebankProcess

MOUNTEBANK_URL = "localhost:2525"

user_one = dict(id=None, login="maury@aol.com", email="maury@aol.com", mobilePhone=None, firstName='A', lastName='A')
user_two = dict(id=None, login="gary@aol.com", email="gary@aol.com", mobilePhone="234-567-8901", firstName='A', lastName='A')
user_three = dict(id="00001", login="dave@aol.com", email="dave@aol.com", mobilePhone="123-456-7890", firstName='A', lastName='A')
user_four = dict(id=None, login="harry@aol.com", email="harry@aol.com", mobilePhone="345-6789-0123", firstName='A', lastName='A')
user_three_okta_json = {
    "id": user_three.get('id'),
    "profile": {
        "login": user_three.get('login'),
        "mobilePhone": user_three.get('mobilePhone'),
        "firstName": user_three.get('firstName'),
        "lastName": user_three.get('lastName'),
        "email": user_three.get('email')
    }
}

class TestUserBroker(unittest.TestCase):
    def setUp(self):
        self.mb = MountebankProcess()
        api_client = ApiClient()
        self.broker = UserBroker(api_client)

    def tearDown(self):
        self.mb.destroy_all_imposters()

    def test_create_new_user_with_invalid_data(self):
        response = self.broker.upsert_user(user_one)
        self.assertEqual(response, 'Invalid user data')

    def test_create_new_user_with_valid_data(self):
        self.setup_imposter('create_new_user.json')
        user, code = self.broker.upsert_user(user_two)
        self.assertEqual(code, 200)
        self.assertEqual(user['id'], "00002")
        self.assertEqual(user['profile']['login'], user_two.get('login'))
        self.assertEqual(user['profile']['mobilePhone'], user_two.get('mobilePhone'))

    def test_update_existing_user_with_id(self):
        self.setup_imposter('update_existing_user.json')
        user, code = self.broker.upsert_user(user_three)
        self.assertEqual(code, 200)
        self.assertEqual(user['id'], user_three.get('id'))
        self.assertEqual(user['profile']['login'], user_three.get('login'))
        self.assertEqual(user['profile']['mobilePhone'], user_three.get('mobilePhone'))

    def test_update_existing_user_with_id_with_okta_json(self):
        self.setup_imposter('update_existing_user.json')
        user, code = self.broker.update_user(user_three_okta_json)
        self.assertEqual(code, 200)
        self.assertEqual(user['id'], user_three.get('id'))
        self.assertEqual(user['profile']['login'], user_three.get('login'))
        self.assertEqual(user['profile']['mobilePhone'], user_three.get('mobilePhone'))

    def test_update_existing_user_without_id(self):
        self.setup_imposter('update_existing_user.json')
        user, code = self.broker.upsert_user(user_four)
        self.assertEqual(code, 200)
        self.assertEqual(user['id'], "00003")
        self.assertEqual(user['profile']['login'], user_four.get('login'))
        self.assertEqual(user['profile']['mobilePhone'], user_four.get('mobilePhone'))

    def test_get_user_method(self):
        self.setup_imposter('update_existing_user.json')
        user = self.broker.get_user(user_four.get('login'))
        self.assertEqual(user['profile']['login'], user_four.get('login'))

    def test_get_user_id_method(self):
        self.setup_imposter('update_existing_user.json')
        user_id = self.broker.get_user_id(user_four.get('login'))
        self.assertEqual(user_id, '00003')

    def setup_imposter(self, file_name):
        file_path = 'test_user_broker/stubs/' + file_name
        imposter = self.mb.create_imposter(file_path)
        self.broker._api_client = ApiClient(BASE_URL=self.mb.get_imposter_url(imposter), API_TOKEN='1')

if __name__ == '__main__':
    unittest.main()

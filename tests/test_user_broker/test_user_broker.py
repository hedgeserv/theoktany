import unittest

from theoktany.user_broker import UserBroker
from theoktany.client import ApiClient
from tests.mb_wrapper import MountebankProcess

MOUNTEBANK_URL = "localhost:2525"

user_one = dict(id=None, login="maury@aol.com", email="maury@aol.com", mobile_phone=None, first_name='A', last_name='A')
user_two = dict(
    id=None, login="gary@aol.com", email="gary@aol.com", mobile_phone="234-567-8901", first_name='A', last_name='A')
user_three = dict(
    id="00001", login="dave@aol.com", email="dave@aol.com", mobile_phone="123-456-7890", first_name='A', last_name='A')
user_four = dict(
    id=None, login="harry@aol.com", email="harry@aol.com", mobile_phone="345-6789-0123", first_name='A', last_name='A')
user_five = {
    'id': None, 'login': 'not-in-okta@aol.com', 'email': "not-in-okta@aol.com", 'mobile_phone': "345-6789-0123",
    'first_name': 'A', 'last_name': 'A'}
user_six = {
    'id': None, 'login': 'factors-fail@aol.com', 'email': "factors-fail@aol.com", 'mobile_phone': "345-6789-0123",
    'first_name': 'A', 'last_name': 'A'}


class TestUserBroker(unittest.TestCase):
    def setUp(self):
        self.mb = MountebankProcess()
        api_client = ApiClient()
        self.broker = UserBroker(api_client)

    def tearDown(self):
        self.mb.destroy_all_imposters()

    def test_create_new_user_with_invalid_data(self):
        with self.assertRaises(AssertionError):
            self.broker.create_user(user_one)

    def test_create_new_user_with_valid_data(self):
        self.setup_imposter('create_new_user.json')
        user = self.broker.create_user(user_two)
        self.assertIsNotNone(user)
        self.assertEqual(user['id'], "00002")
        self.assertEqual(user['login'], user_two.get('login'))
        self.assertEqual(user['mobile_phone'], user_two.get('mobile_phone'))

    def test_update_existing_user_with_id(self):
        self.setup_imposter('update_existing_user.json')
        user = self.broker.update_user_phone_number(user_three['id'], user_three['mobile_phone'])
        self.assertIsNotNone(user)
        self.assertEqual(user['id'], user_three.get('id'))
        self.assertEqual(user['login'], user_three.get('login'))
        self.assertEqual(user['mobile_phone'], user_three.get('mobile_phone'))

    def test_update_existing_user_without_id_or_phone(self):
        with self.assertRaises(AssertionError):
            self.broker.update_user_phone_number(user_two['id'], user_two['mobile_phone'])
        with self.assertRaises(AssertionError):
            self.broker.update_user_phone_number(user_three['id'], None)

    def test_get_user_method(self):
        self.setup_imposter('update_existing_user.json')
        user = self.broker.get_user(user_four.get('login'))
        self.assertEqual(user['login'], user_four.get('login'))

        self.assertIn('factors', user)
        self.assertEqual(len(user['factors']), 1)
        self.assertEqual(user['factors'][0]['phone_number'], user_four['mobile_phone'])

    def test_get_user_fail(self):
        self.setup_imposter('update_existing_user.json')
        self.assertIsNone(self.broker.get_user(user_five.get('login')))

    def test_get_user_factors_fail(self):
        self.setup_imposter('update_existing_user.json')
        self.assertIsNone(self.broker.get_user(user_six.get('login')))

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

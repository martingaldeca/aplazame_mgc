import json
import uuid

from django.db.transaction import TransactionManagementError

from apps.finance.models import Action, Wallet
from apps.finance.factories import WalletFactory
from django.test import TransactionTestCase

from rest_framework.reverse import reverse

from rest_framework.test import APIClient


class TestAddFundsApi(TransactionTestCase):

    def setUp(self):
        super().setUp()
        self.wallet = WalletFactory.create(balance=500.00)
        self.request = APIClient()
        self.url = reverse('add-funds')

    def tearDown(self) -> None:
        try:
            Action.objects.all().delete()
            Wallet.objects.all().delete()
        except TransactionManagementError:
            pass
        return super().tearDown()

    def test_successfully_add_funds(self):
        body = {
            "amount_to_add": 500.00,
            "token": str(self.wallet.token),
            "comment": "Add test"
        }
        body_as_json = json.dumps(body)
        obtained_response = self.request.post(self.url, data=body_as_json, content_type='application/json')
        self.assertEqual(202, obtained_response.status_code, "The post was ok.")

        self.wallet.refresh_from_db()
        self.assertAlmostEqual(1000, self.wallet.balance, msg="Correct balance.")

    def test_bad_token_add_funds_api(self):
        body = {
            "amount_to_add": 500.00,
            "token": 'bad_token',
            "comment": "Add test"
        }
        body_as_json = json.dumps(body)
        obtained_response = self.request.post(self.url, data=body_as_json, content_type='application/json')
        self.assertEqual(406, obtained_response.status_code, "Wrong token.")
        self.assertEqual("WrongTokenError, The wallet with token 'bad_token' has a bad format. ", obtained_response.data['error'])
        uuid_to_use = str(uuid.uuid1())
        body = {
            "amount_to_add": 500.00,
            "token": uuid_to_use,
            "comment": "Add test"
        }
        body_as_json = json.dumps(body)
        obtained_response = self.request.post(self.url, data=body_as_json, content_type='application/json')
        self.assertEqual(406, obtained_response.status_code, "Wrong token.")
        self.assertEqual(f"WrongTokenError, The wallet with token '{uuid_to_use}' does not exists. ", obtained_response.data['error'])

    def test_invalid_amount_to_add_api(self):
        body = {
            "amount_to_add": -500.00,
            "token": str(self.wallet.token),
            "comment": "Add test"
        }
        body_as_json = json.dumps(body)
        obtained_response = self.request.post(self.url, data=body_as_json, content_type='application/json')
        self.assertEqual(406, obtained_response.status_code, "Invalid amount.")
        self.assertEqual(f"InvalidAmount, The amount '-500.0' must be positive. ", obtained_response.data['error'])

    def test_not_all_need_fields_posted(self):
        body = {
            "token": str(self.wallet.token),
            "comment": "Add test"
        }
        body_as_json = json.dumps(body)
        obtained_response = self.request.post(self.url, data=body_as_json, content_type='application/json')
        self.assertEqual(400, obtained_response.status_code, "Not all needed fields posted.")
        self.assertEqual(f"The post need the fields ['amount_to_add', 'token'] but did not pass ['amount_to_add'] fields.", obtained_response.data['error'])
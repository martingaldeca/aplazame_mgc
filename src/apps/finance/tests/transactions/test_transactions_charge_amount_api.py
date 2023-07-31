import json
import uuid
from django.db.transaction import TransactionManagementError
from apps.finance.models import Action, Wallet
from apps.finance.factories import WalletFactory
from django.test import TransactionTestCase
from rest_framework.reverse import reverse
from rest_framework.test import APIClient
from apps.core.factories import UserProfileFactory
from apps.core.models import UserTypes


class TestChargeAmountApi(TransactionTestCase):

    def setUp(self):
        super().setUp()
        self.start_commerce_funds = 0.0
        self.commerce_user_profile = UserProfileFactory.create(user_type=UserTypes.commerce)
        self.commerce_wallet = WalletFactory.create(balance=self.start_commerce_funds, user=self.commerce_user_profile.user, token=uuid.uuid4())
        self.start_customer_funds = 1001.0
        self.customer_user_profile = UserProfileFactory.create(user_type=UserTypes.customer)
        self.customer_wallet = WalletFactory.create(balance=self.start_customer_funds, user=self.customer_user_profile.user)
        self.request = APIClient()
        self.url = reverse('add-charge')

    def tearDown(self) -> None:
        try:
            Action.objects.all().delete()
            Wallet.objects.all().delete()
        except TransactionManagementError:
            pass
        return super().tearDown()

    def test_successfully_add_funds(self):
        body = {
            "amount_to_charge": 1000.00,
            "creditor_token": str(self.commerce_wallet.token),
            "debtor_token": str(self.customer_wallet.token),
            "comment": "Add test"
        }
        body_as_json = json.dumps(body)
        obtained_response = self.request.post(self.url, data=body_as_json, content_type='application/json')
        self.assertEqual(202, obtained_response.status_code, "The post was ok.")

        self.commerce_wallet.refresh_from_db()
        self.customer_wallet.refresh_from_db()
        self.assertAlmostEqual(1000, self.commerce_wallet.balance, msg="Correct balance.")
        self.assertAlmostEqual(1, self.customer_wallet.balance, msg="Correct balance.")

    def test_bad_token_add_charge_api(self):
        body = {
            "amount_to_charge": 1000.00,
            "creditor_token": 'Soy un token malvado',
            "debtor_token": str(self.customer_wallet.token),
            "comment": "Add test"
        }
        body_as_json = json.dumps(body)
        obtained_response = self.request.post(self.url, data=body_as_json, content_type='application/json')
        self.assertEqual(406, obtained_response.status_code, "Wrong token.")
        self.assertEqual(
            f"WrongTokenError, The wallet with token 'Soy un token malvado' or "
            f"token '{str(self.customer_wallet.token)}' has a bad format. ", obtained_response.data['error']
        )
        uuid_to_use = str(uuid.uuid1())
        body = {
            "amount_to_charge": 1000.00,
            "creditor_token": uuid_to_use,
            "debtor_token": str(self.customer_wallet.token),
            "comment": "Add test"
        }
        body_as_json = json.dumps(body)
        obtained_response = self.request.post(self.url, data=body_as_json, content_type='application/json')
        self.assertEqual(406, obtained_response.status_code, "Wrong token.")
        self.assertEqual(
            f"WrongTokenError, The wallet with token '{uuid_to_use}' or "
            f"token '{str(self.customer_wallet.token)}' does not exists. ", obtained_response.data['error']
        )

    def test_invalid_amount_to_charge_api(self):
        body = {
            "amount_to_charge": -1000.00,
            "creditor_token": str(self.commerce_wallet.token),
            "debtor_token": str(self.customer_wallet.token),
            "comment": "Add test"
        }
        body_as_json = json.dumps(body)
        obtained_response = self.request.post(self.url, data=body_as_json, content_type='application/json')
        self.assertEqual(406, obtained_response.status_code, "Invalid amount.")
        self.assertEqual(
            "InvalidAmount, Trying to charge negative amount to the wallet funds ['-1000.0'], this is not allowed. ",
            obtained_response.data['error'],
        )

    def test_not_all_need_fields_posted(self):
        body = {
            "creditor_token": str(self.commerce_wallet.token),
            "debtor_token": str(self.customer_wallet.token),
            "comment": "Add test"
        }
        body_as_json = json.dumps(body)
        obtained_response = self.request.post(self.url, data=body_as_json, content_type='application/json')
        self.assertEqual(400, obtained_response.status_code, "Not all needed fields posted.")
        self.assertEqual(
            "The post need the fields ['amount_to_charge', 'creditor_token', 'debtor_token'] but did not pass ['amount_to_charge'] fields.",
            obtained_response.data['error'],
        )

    def test_not_commerce_charge_api(self):
        body = {
            "amount_to_charge": 1000.00,
            "debtor_token": str(self.commerce_wallet.token),
            "creditor_token": str(self.customer_wallet.token),
            "comment": "Add test"
        }
        body_as_json = json.dumps(body)
        obtained_response = self.request.post(self.url, data=body_as_json, content_type='application/json')
        self.assertEqual(406, obtained_response.status_code, "Not commerce error.")

    def test_insufficient_funds_api(self):
        body = {
            "amount_to_charge": 10000.00,
            "creditor_token": str(self.commerce_wallet.token),
            "debtor_token": str(self.customer_wallet.token),
            "comment": "Add test"
        }
        body_as_json = json.dumps(body)
        obtained_response = self.request.post(self.url, data=body_as_json, content_type='application/json')
        self.assertEqual(402, obtained_response.status_code, "Insufficient funds.")

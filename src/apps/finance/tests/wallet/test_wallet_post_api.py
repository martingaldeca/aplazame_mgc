import json

from django.db.transaction import TransactionManagementError

from apps.finance.models import Wallet
from django.test import TransactionTestCase

from rest_framework.reverse import reverse

from rest_framework.test import APIClient


class TestWalletPostApi(TransactionTestCase):

    def setUp(self):
        super().setUp()
        self.request = APIClient()
        self.url = reverse('list-wallets')

    def tearDown(self) -> None:
        try:
            Wallet.objects.all().delete()
        except TransactionManagementError:
            pass
        return super().tearDown()

    def test_wallet_post_are_not_allowed(self):
        body = {
            "Wallet": [
                {
                    "user": "username",
                    "balance": 500
                },
            ]
        }
        body_as_json = json.dumps(body)
        obtained_response = self.request.post(self.url, data=body_as_json, content_type='application/json')
        self.assertEqual(403, obtained_response.status_code, "Posts for wallet model are not allowed.")

from apps.finance.models import Wallet
from django.test import TransactionTestCase

from rest_framework.reverse import reverse

from apps.finance.factories import *
from urllib.parse import urlencode, urljoin
from rest_framework.test import APIClient


class TestWalletGetApi(TransactionTestCase):

    def setUp(self):
        super().setUp()
        self.request = APIClient()
        self.raw_url = reverse('list-wallets')
        self.query_params = {'limit': 10, 'offset': 0, 'page': 1}
        self.real_url = urljoin(self.raw_url, f'?{urlencode(self.query_params)}')
        self.wallet = WalletFactory.create()

    def tearDown(self) -> None:
        Wallet.objects.all().delete()
        return super().tearDown()

    def test_wallet_get(self):
        """
        Test to check that the users get is working properly.
        """
        self.assertNotEqual(self.raw_url, None, "Url reverse must be ok.")

        obtained_response = self.request.get(self.real_url)
        results = obtained_response.data['results']
        self.assertEqual(self.wallet.user.username, results[0]['user']['username'], "The get response is correct.")

    def test_wallet_limit_get(self):
        """
        Test to check that the pagination works properly
        :return:
        """
        for _ in range(50):
            WalletFactory.create()
        obtained_response = self.request.get(self.real_url)
        results = obtained_response.data['results']
        self.assertEqual(10, len(results), "Limit in get for user_profile works properly.")

    def test_wallet_counter(self):
        """
        Test to check that the counter works properly
        :return:
        """
        for _ in range(50):
            WalletFactory.create()
        obtained_response = self.request.get(self.real_url)
        count = obtained_response.data['count']
        self.assertEqual(51, count, "Counter in get for user_profile works properly.")


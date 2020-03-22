from django.contrib.auth.models import User
from django.db.transaction import TransactionManagementError

from apps.finance.models import Action, Wallet
from django.test import TransactionTestCase

from rest_framework.reverse import reverse

from apps.finance.factories import *
from urllib.parse import urlencode, urljoin
from rest_framework.test import APIClient

from apps.core.models import UserProfile


class TestActionGetApi(TransactionTestCase):

    def setUp(self):
        super().setUp()
        self.request = APIClient()
        self.raw_url = reverse('list-actions')
        self.query_params = {'limit': 10, 'offset': 0, 'page': 1}
        self.real_url = urljoin(self.raw_url, f'?{urlencode(self.query_params)}')
        self.action = ActionFactory.create()

    def tearDown(self) -> None:
        try:
            Action.objects.all().delete()
            Wallet.objects.all().delete()
            User.objects.all().delete()
            UserProfile.objects.all().delete()
        except TransactionManagementError:
            pass
        return super().tearDown()

    def test_action_get(self):
        """
        Test to check that the users get is working properly.
        """
        self.assertNotEqual(self.raw_url, None, "Url reverse must be ok.")

        obtained_response = self.request.get(self.real_url)
        results = obtained_response.data['results']
        self.assertEqual(self.action.created_by.username, results[0]['created_by']['username'], "The get response is correct.")

    def test_action_limit_get(self):
        """
        Test to check that the pagination works properly
        :return:
        """
        for i in range(50):
            ActionFactory.create()
        obtained_response = self.request.get(self.real_url)
        results = obtained_response.data['results']
        self.assertEqual(10, len(results), "Limit in get for user_profile works properly.")

    def test_action_counter(self):
        """
        Test to check that the counter works properly
        :return:
        """
        for i in range(50):
            ActionFactory.create()
        obtained_response = self.request.get(self.real_url)
        count = obtained_response.data['count']
        self.assertEqual(51, count, "Counter in get for user_profile works properly.")


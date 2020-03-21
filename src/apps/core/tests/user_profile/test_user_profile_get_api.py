from apps.core.models import UserProfile
from django.test import TestCase

from rest_framework.reverse import reverse

from apps.core.factories import *
from urllib.parse import urlencode, urljoin
from rest_framework.test import APIClient


class TestUserProfileGetApi(TestCase):

    def setUp(self):
        super().setUp()
        self.request = APIClient()
        self.raw_url = reverse('list-users')
        self.query_params = {'limit': 10, 'offset': 0, 'page': 1}
        self.real_url = urljoin(self.raw_url, f'?{urlencode(self.query_params)}')
        self.user_profile = UserProfileFactory()

    def tearDown(self) -> None:
        UserProfile.objects.all().delete()
        return super().tearDown()

    def test_user_profile_get(self):
        """
        Test to check that the users get is working properly.
        """
        self.assertNotEqual(self.raw_url, None, "Url reverse must be ok.")

        obtained_response = self.request.get(self.real_url)
        results = obtained_response.data['results']
        self.assertEqual(self.user_profile.user.username, results[0]['user']['username'], "The get response is correct.")

    def test_user_profile_limit_get(self):
        """
        Test to check that the pagination works properly
        :return:
        """
        for i in range(50):
            UserProfileFactory()
        obtained_response = self.request.get(self.real_url)
        results = obtained_response.data['results']
        self.assertEqual(10, len(results), "Limit in get for user_profile works properly.")

    def test_user_profile_counter(self):
        """
        Test to check that the counter works properly
        :return:
        """
        for i in range(50):
            UserProfileFactory()
        obtained_response = self.request.get(self.real_url)
        count = obtained_response.data['count']
        self.assertEqual(51, count, "Counter in get for user_profile works properly.")

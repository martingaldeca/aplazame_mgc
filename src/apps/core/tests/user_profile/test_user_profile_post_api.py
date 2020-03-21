import json

from django.db.transaction import TransactionManagementError

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
        self.url = reverse('list-users')

    def tearDown(self) -> None:
        try:
            UserProfile.objects.all().delete()
        except TransactionManagementError:
            pass
        return super().tearDown()

    def test_create_user(self):
        body = {
            "UserProfile": [
                {
                    "user": "username",
                    "user__email": "soyunmail@mail.com",
                    "user_type": 2
                }
            ]
        }
        body_as_json = json.dumps(body)
        obtained_response = self.request.post(self.url, data=body_as_json, content_type='application/json')
        self.assertEqual(1, obtained_response.data['total_created'], "Will create one item in the database.")
        user_profile_created = UserProfile.objects.get(id=obtained_response.data['ids_created'][0])
        self.assertEqual(2, user_profile_created.user_type)

    def test_create_multiple_users(self):

        body = {
            "UserProfile": [
                {
                    "user": "username1",
                    "user__email": "soyunmail1@mail.com",
                    "user_type": 2
                },
                {
                    "user": "username2",
                    "user__email": "soyunmail2@mail.com",
                    "user_type": 2
                },
            ]
        }
        body_as_json = json.dumps(body)
        obtained_response = self.request.post(self.url, data=body_as_json, content_type='application/json')
        self.assertEqual(2, obtained_response.data['total_created'], "Will create 2 items in the database.")

        # Check that there is not any raise here
        for created_id in obtained_response.data['ids_created']:
            UserProfile.objects.get(id=created_id)

    def test_crash_if_user_exists(self):
        body = {
            "UserProfile": [
                {
                    "user": "username",
                    "user__email": "soyunmail@mail.com",
                    "user__first_name": "name",
                    "user__last_name": "second_name",
                    "user_type": 2
                },
                {
                    "user": "username",
                    "user__email": "soyunmail@mail.com",
                    "user_type": 2
                }
            ]
        }
        body_as_json = json.dumps(body)
        obtained_response = self.request.post(self.url, data=body_as_json, content_type='application/json')
        self.assertEqual(409, obtained_response.status_code, "Will crash if try to post same object twice")

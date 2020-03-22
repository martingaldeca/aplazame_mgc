import json

from django.db.transaction import TransactionManagementError

from apps.finance.models import Action
from django.test import TransactionTestCase

from rest_framework.reverse import reverse

from rest_framework.test import APIClient


class TestActionPostApi(TransactionTestCase):

    def setUp(self):
        super().setUp()
        self.request = APIClient()
        self.url = reverse('list-actions')

    def tearDown(self) -> None:
        try:
            Action.objects.all().delete()
        except TransactionManagementError:
            pass
        return super().tearDown()

    def test_action_post_are_not_allowed(self):
        body = {
            "Action": [
                {
                    "created_by": "username",
                    "delta": 500
                },
            ]
        }
        body_as_json = json.dumps(body)
        obtained_response = self.request.post(self.url, data=body_as_json, content_type='application/json')
        self.assertEqual(403, obtained_response.status_code, "Posts for action model are not allowed.")

from django.test import TestCase
import logging

from apps.core.factories import UserProfileFactory
from apps.core.models import UserTypes

logger = logging.getLogger(__name__)


class TestUserProfile(TestCase):

    def setUp(self) -> None:
        self.user_profile = UserProfileFactory()
        super().setUp()

    def tearDown(self) -> None:
        super().tearDown()

    def test_creation_user_profile(self):
        self.assertEquals(self.user_profile.user_type, UserTypes.customer, "The default user type is customer")

    def test_change_user_type(self):
        self.user_profile.change_user_type(2)
        self.assertEquals(self.user_profile.user_type, UserTypes.commerce)

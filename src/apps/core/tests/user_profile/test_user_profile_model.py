from django.contrib.auth.models import User
from django.db.transaction import TransactionManagementError
from django.test import TransactionTestCase
import logging

from apps.core.factories import UserProfileFactory
from apps.core.models import UserTypes
from apps.core.models import UserProfile

logger = logging.getLogger(__name__)


class TestUserProfile(TransactionTestCase):

    def setUp(self) -> None:
        self.user_profile = UserProfileFactory.create()
        super().setUp()

    def tearDown(self) -> None:
        try:
            User.objects.all().delete()
            UserProfile.objects.all().delete()
        except TransactionManagementError:
            pass
        return super().tearDown()

    def test_creation_user_profile(self):
        self.assertEquals(self.user_profile.user_type, UserTypes.customer, "The default user type is customer")

    def test_change_user_type(self):
        self.user_profile.change_user_type(2)
        self.assertEquals(self.user_profile.user_type, UserTypes.commerce)

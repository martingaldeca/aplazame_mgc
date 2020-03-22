from django.contrib.auth.models import User
from django.db.transaction import TransactionManagementError
from django.test import TransactionTestCase
import logging
from apps.finance.factories import ActionFactory
from apps.finance.models import Action, ValidActions, Wallet
from apps.core.models import UserProfile

logger = logging.getLogger(__name__)


class TestAction(TransactionTestCase):

    def setUp(self) -> None:
        self.action = ActionFactory.create()
        super().setUp()

    def tearDown(self) -> None:
        try:
            Action.objects.all().delete()
            Wallet.objects.all().delete()
            User.objects.all().delete()
            UserProfile.objects.all().delete()
        except TransactionManagementError:
            pass
        return super().tearDown()

    def test_creation_wallet(self):
        self.assertEquals(self.action.action_type, ValidActions.deposit, "The default action is deposit.")

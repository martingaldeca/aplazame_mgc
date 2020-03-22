from django.db.transaction import TransactionManagementError
from django.test import TestCase
import logging
from apps.finance.factories import ActionFactory
from apps.finance.models import Action, ValidActions

logger = logging.getLogger(__name__)


class TestAction(TestCase):

    def setUp(self) -> None:
        self.action = ActionFactory.create()
        super().setUp()

    def tearDown(self) -> None:
        try:
            Action.objects.all().delete()
        except TransactionManagementError:
            pass
        super().tearDown()

    def test_creation_wallet(self):
        self.assertEquals(self.action.action_type, ValidActions.deposit, "The default action is deposit.")

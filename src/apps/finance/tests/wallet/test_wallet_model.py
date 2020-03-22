from django.db.transaction import TransactionManagementError
from django.test import TestCase
import logging
from apps.finance.factories import WalletFactory
from apps.finance.models import ValidCurrencies, Action, Wallet

logger = logging.getLogger(__name__)


class TestWallet(TestCase):

    def setUp(self) -> None:
        self.start_funds = 3.14
        self.wallet = WalletFactory.create(balance=self.start_funds)
        super().setUp()

    def tearDown(self) -> None:
        try:
            Action.objects.all().delete()
            Wallet.objects.all().delete()
        except TransactionManagementError:
            pass
        super().tearDown()

    def test_creation_wallet(self):
        self.assertEquals(self.wallet.currency, ValidCurrencies.EUR, "The default currency is euro.")

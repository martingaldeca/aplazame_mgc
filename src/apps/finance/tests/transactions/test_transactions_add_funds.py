from decimal import Decimal
import threading

from django.db.transaction import TransactionManagementError
from django.test import TransactionTestCase
import logging
from apps.finance.transactions import add_funds
from apps.finance.factories import WalletFactory
from apps.finance.models import Action, ValidActions, Wallet
from apps.finance.exceptions import WrongTokenError, InvalidAmount

logger = logging.getLogger(__name__)


class TestTransactionsAddFunds(TransactionTestCase):

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

    def test_add_funds(self):
        with self.assertRaises(WrongTokenError):
            add_funds(token='FAKE_TOKEN')
        with self.assertRaises(WrongTokenError):
            add_funds(token='06335e84-2872-4914-8c5d-3ed07d2a2f16')
        with self.assertRaises(InvalidAmount):
            add_funds(token=str(self.wallet.token), amount_to_add=-5)

        add_funds(token=str(self.wallet.token), amount_to_add=1000, comment="Adding funds to the wallet.")

        # Must update the model from the db
        self.wallet.refresh_from_db()
        self.assertAlmostEqual(Decimal(1000 + self.start_funds), self.wallet.balance, msg="Correct add funds.")

        actions = Action.objects.all()
        self.assertEqual(1, actions.count(), msg="One action generated.")
        self.assertEqual(self.wallet, actions[0].wallet, msg="Correct action associate to the wallet.")
        self.assertAlmostEqual(Decimal(1000), actions[0].delta, msg="Correct delta action.")
        self.assertEqual(ValidActions.deposit, actions[0].action_type, msg="Correct action type.")
        self.assertEqual("Adding funds to the wallet.", actions[0].comment, msg="Correct action comment.")

    def test_atomic_funds(self):
        """
        Test to check that the transactions over the database are atomic
        :return:
        """
        t1 = threading.Thread(
            target=add_funds,
            kwargs={'token': str(self.wallet.token), 'amount_to_add': 1000, 'test_sleep_time': 1}
        )
        t2 = threading.Thread(
            target=add_funds,
            kwargs={'token': str(self.wallet.token), 'amount_to_add': 1000, 'test_sleep_time': 0.5}
        )
        t1.start()
        t2.start()
        t1.join()
        t2.join()
        self.wallet.refresh_from_db()
        self.assertAlmostEqual(Decimal(2000 + self.start_funds), self.wallet.balance, msg="Atomic transactions")
        actions = Action.objects.all()
        self.assertEqual(2, actions.count(), msg="Two action generated.")

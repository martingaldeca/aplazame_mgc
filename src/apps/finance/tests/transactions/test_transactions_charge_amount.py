import uuid
from decimal import Decimal
import threading
from apps.core.models import UserTypes
from apps.core.exceptions import NotCommerceError

from django.db.transaction import TransactionManagementError
from django.test import TransactionTestCase
import logging
from apps.finance.transactions import add_charge
from apps.finance.factories import WalletFactory
from apps.finance.models import Action, Wallet
from apps.finance.exceptions import WrongTokenError, InvalidAmount, InsufficientFundsException
from apps.core.factories import UserProfileFactory

logger = logging.getLogger(__name__)


class TestTransactionsChargeAmount(TransactionTestCase):

    def setUp(self) -> None:
        self.start_commerce_funds = 0.0
        self.commerce_user_profile = UserProfileFactory.create(user_type=UserTypes.commerce)
        self.commerce_wallet = WalletFactory.create(balance=self.start_commerce_funds, user=self.commerce_user_profile.user, token=uuid.uuid4())
        self.start_customer_funds = 1001.0
        self.customer_user_profile = UserProfileFactory.create(user_type=UserTypes.customer)
        self.customer_wallet = WalletFactory.create(balance=self.start_customer_funds, user=self.customer_user_profile.user)
        super().setUp()

    def tearDown(self) -> None:
        try:
            Action.objects.all().delete()
            Wallet.objects.all().delete()
        except TransactionManagementError:
            pass
        super().tearDown()

    def test_add_charge(self):
        with self.assertRaises(WrongTokenError):
            add_charge(
                amount_to_charge=1000, creditor_token='FAKE_TOKEN', debtor_token='06335e84-2872-4914-8c5d-3ed07d2a2f16', comment='TROLOLOLO charge'
            )
        with self.assertRaises(WrongTokenError):
            add_charge(
                amount_to_charge=1000, creditor_token='06335e84-2872-4914-8c5d-3ed07d2a2f16',
                debtor_token='06335e84-2872-4914-8c5d-3ed07d2a2f16', comment='TROLOLOLO charge'
            )
        with self.assertRaises(NotCommerceError):
            add_charge(
                amount_to_charge=1000, creditor_token=str(self.customer_wallet.token),
                debtor_token=str(self.commerce_wallet.token), comment='TROLOLOLO charge'
            )
        with self.assertRaises(WrongTokenError):
            add_charge(
                amount_to_charge=1000, creditor_token=str(self.commerce_wallet.token),
                debtor_token=str(self.commerce_wallet.token), comment='TROLOLOLO charge'
            )
        with self.assertRaises(InvalidAmount):
            add_charge(
                amount_to_charge=-1000, creditor_token=str(self.commerce_wallet.token),
                debtor_token=str(self.customer_wallet.token), comment='TROLOLOLO charge'
            )

        add_charge(
            amount_to_charge=1000, creditor_token=str(self.commerce_wallet.token),
            debtor_token=str(self.customer_wallet.token), comment='TROLOLOLO charge'
        )

        # Refresh the objects from the database
        self.commerce_wallet.refresh_from_db()
        self.customer_wallet.refresh_from_db()
        self.assertAlmostEqual(Decimal(1000 + self.start_commerce_funds), self.commerce_wallet.balance, msg="Correct balance for commerce.")
        self.assertAlmostEqual(Decimal(self.start_customer_funds - 1000), self.customer_wallet.balance, msg="Correct balance for commerce.")

        with self.assertRaises(InsufficientFundsException):
            add_charge(
                amount_to_charge=1000, creditor_token=str(self.commerce_wallet.token),
                debtor_token=str(self.customer_wallet.token), comment='TROLOLOLO charge'
            )

        # Check the generated actions
        actions = Action.objects.all()
        self.assertEqual(2, actions.count(), "All actions generated.")

        # Check the amounts of the transactions
        action_debtor = actions.get(wallet=self.customer_wallet)
        self.assertAlmostEqual(Decimal(-1000), action_debtor.delta, msg="Charge action ok for debtor.")
        action_creditor = actions.get(wallet=self.commerce_wallet)
        self.assertAlmostEqual(Decimal(1000), action_creditor.delta, msg="Charge action ok for creditor.")

    def test_atomic_charges(self):
        """
        Test to check that the transactions over the database are atomic
        :return:
        """
        t1 = threading.Thread(
            target=add_charge,
            kwargs={
                'amount_to_charge': 10, 'creditor_token': str(self.commerce_wallet.token),
                'debtor_token': str(self.customer_wallet.token), 'comment': 'TROLOLOLO charge',
                'test_sleep_time': 1.5
            }
        )
        t2 = threading.Thread(
            target=add_charge,
            kwargs={
                'amount_to_charge': 1000, 'creditor_token': str(self.commerce_wallet.token),
                'debtor_token': str(self.customer_wallet.token), 'comment': 'TROLOLOLO charge',
                'test_sleep_time': 0.5
            }
        )
        t1.start()
        t2.start()
        t1.join()
        t2.join()

        # The fastest transaction will be done, but the other will not
        # Refresh the objects from the database
        self.commerce_wallet.refresh_from_db()
        self.customer_wallet.refresh_from_db()
        self.assertAlmostEqual(Decimal(1000 + self.start_commerce_funds), self.commerce_wallet.balance, msg="Correct balance for commerce.")
        self.assertAlmostEqual(Decimal(self.start_customer_funds - 1000), self.customer_wallet.balance, msg="Correct balance for commerce.")


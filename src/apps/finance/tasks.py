import random
import uuid

from apps.finance.models import Wallet, Action, ValidCurrencies, ValidActions
from celery import task
from logging import getLogger
from apps.finance.factories import WalletFactory, ActionFactory
from apps.core.factories import UserProfileFactory
from apps.core.models import UserTypes
from apps.finance.transactions import add_funds, add_charge

logger = getLogger(__name__)


@task(bind=True)
def check_integrity(self):
    """
    Function to check the integrity of the all wallet balances
    :return:
    """

    wallets = Wallet.objects.all()
    for wallet in wallets:
        final_balance = 0
        wallet_actions = Action.objects.filter(wallet=wallet).exclude(action_type=ValidActions.insufficient_funds)
        for wallet_action in wallet_actions:
            final_balance += wallet_action.delta
            logger.info(f"Final balance for wallet is {final_balance}")

        if final_balance != wallet.balance:
            logger.error(f"The wallet '{wallet.id}' has a bad balance, from total transactions should be {final_balance} but is {wallet.balance}")
            wallet.set_corrupted()


@task(bind=True)
def populate_database_for_test(self):
    """
    Function for populate the database with fake data for the technical test for aplazame
    :param self:
    :return:
    """

    # We will generate 5000 customer wallets with 5000 actions each from 100 commerce users
    possible_transactions = {
        'charge': {
            'function': add_charge,
            'parameter': 'charge_parameters'
        },
        'deposit': {
            'function': add_funds,
            'parameter': 'deposit_parameters'
        }
    }
    commerce_wallets = []
    for _ in range(100):
        commerce_user = UserProfileFactory.create(user_type=UserTypes.commerce)
        commerce_wallets.append(WalletFactory.create(
            user=commerce_user.user, token=uuid.uuid4(),
            balance=0.0,
            currency=random.choice([currency[0] for currency in ValidCurrencies])
        ))

    for _ in range(5000):
        customer_user = UserProfileFactory.create(user_type=UserTypes.customer)
        customer_wallet = (WalletFactory.create(
            user=customer_user.user, token=uuid.uuid4(),
            balance=0.0,
            currency=random.choice([currency[0] for currency in ValidCurrencies])
        ))

        for _ in range(5000):
            transaction_parameters = {
                'charge_parameters': {
                    'amount_to_charge': random.uniform(0, 10000000),
                    'creditor_token': str(random.choice(commerce_wallets).token),
                    'debtor_token': str(customer_wallet.token),
                    'comment': ''
                },
                'deposit_parameters': {
                    'amount_to_add': random.uniform(0, 10000000),
                    'token': str(customer_wallet.token),
                    'comment': ''
                }
            }
            final_transaction = random.choice(list(possible_transactions.keys()))
            transaction_function = possible_transactions[final_transaction]['function']
            transaction_parameter_to_use = transaction_parameters[possible_transactions[final_transaction]['parameter']]
            try:
                transaction_function(**transaction_parameter_to_use)
            except Exception as ex:
                logger.info(ex)

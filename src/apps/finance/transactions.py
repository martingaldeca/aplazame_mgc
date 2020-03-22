from decimal import Decimal

from currency_converter import CurrencyConverter
from datetime import datetime
from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.core.resolvers.user_profile import resolve_user_profile
from apps.core.models import UserTypes

from apps.finance.exceptions import InsufficientFundsException, InvalidAmount, WrongTokenError
from apps.core.exceptions import NotCommerceError
from django.db import transaction
import time
from apps.finance.models import Wallet, Action, ValidActions, ValidCurrencies
from logging import getLogger

logger = getLogger(__name__)
converter = CurrencyConverter()


# TODO migrate this to celery task
def add_funds(amount_to_add: float = 0, token: str = None, comment: str = '', test_sleep_time: int = 0) -> None:
    """
    Function to add funds, this function will only allow to add positive amount.

    The token is unique for each wallet, so we can get the wallet from the token

    This function must be atomic and generate one single action
    :param comment:
    :param test_sleep_time: Time to sleep for tests purposes
    :param token:
    :param amount_to_add:
    :return:
    """
    with transaction.atomic():
        time.sleep(test_sleep_time)
        try:
            wallet = Wallet.objects.select_for_update().get(token=token)
        except Wallet.DoesNotExist:
            message = f"The wallet with token '{token}' does not exists."
            logger.warning(message)
            raise WrongTokenError(message)
        except ValidationError:
            message = f"The wallet with token '{token}' has a bad format."
            logger.warning(message)
            raise WrongTokenError(message)
        if token != wallet.token.__str__():
            # We should never enter here, if is the case it could be a problem with managers
            raise WrongTokenError(f"Token '{token}' invalid for wallet '{wallet.id}'.")
        if amount_to_add < 0:
            logger.warning(f"Trying to add negative amount to the wallet funds ['{amount_to_add}'], this is not allowed.")
            raise InvalidAmount(f"The amount '{amount_to_add}' must be positive.")

        logger.info(f"Wallet '{wallet.id}' will add {amount_to_add} to the funds.")
        wallet.balance += Decimal(amount_to_add)
        wallet.save()

        # Generate the action in the database
        Action(
            created_by=wallet.user,
            created=timezone.now(),
            wallet=wallet,
            action_type=ValidActions.deposit,
            comment=comment,
            delta=amount_to_add
        ).save()


# TODO migrate this to celery task
def add_charge(
        amount_to_charge: float = 0, creditor_token: str = None, debtor_token: str = None, comment: str = '',
        test_sleep_time: int = 0, converter_date: datetime = datetime.now()
):
    """
    Transaction to add a charge to a wallet from other
    :param converter_date: Converter time parameter for tests purposes
    :param amount_to_charge:
    :param creditor_token:
    :param debtor_token:
    :param comment:
    :param test_sleep_time:
    :return:
    """
    with transaction.atomic():
        time.sleep(test_sleep_time)
        # Check that the creditor token is not the debtor token to avoid problems with race conditions and dead locks
        if creditor_token == debtor_token:
            message = "You can not charge to yourself."
            logger.warning(message)
            raise WrongTokenError(message)

        try:
            creditor_wallet = Wallet.objects.select_for_update().get(token=creditor_token)
            debtor_wallet = Wallet.objects.select_for_update().get(token=debtor_token)
        except Wallet.DoesNotExist:
            message = f"The wallet with token '{creditor_token}' or token '{debtor_token}' does not exists."
            logger.warning(message)
            raise WrongTokenError(message)
        except ValidationError:
            message = f"The wallet with token '{creditor_token}' or token '{debtor_token}' has a bad format."
            logger.warning(message)
            raise WrongTokenError(message)

        # Only commerce or admin users can add a charge to another user account
        if resolve_user_profile(user__username=creditor_wallet.user.username).user_type == UserTypes.customer:
            message = (
                f"The user {creditor_wallet.user.id} can not make charges and "
                f"tried to charge {amount_to_charge} {ValidCurrencies.attributes[creditor_wallet.currency]} to user {debtor_wallet.user.id}."
            )
            logger.warning(message)
            raise NotCommerceError(message)

        # Must check that the charge to add is positive
        if amount_to_charge < 0:
            message = f"Trying to charge negative amount to the wallet funds ['{amount_to_charge}'], this is not allowed."
            logger.warning(message)
            raise InvalidAmount(message)

        # Check the currencies and convert if needed
        creditor_amount_to_charge = Decimal(amount_to_charge)
        debtor_amount_to_charge = amount_to_charge
        if debtor_wallet.currency != creditor_wallet.currency:
            # We convert the creditor amount to the debtor amount
            debtor_amount_to_charge = converter.convert(
                amount_to_charge,
                str(ValidCurrencies.attributes[debtor_wallet.currency]),
                str(ValidCurrencies.attributes[creditor_wallet.currency]),
                date=converter_date
            )
        debtor_amount_to_charge = Decimal(debtor_amount_to_charge)

        # Must check that there are enough funds in the debtor wallet
        if debtor_wallet.balance - debtor_amount_to_charge < 0:
            message = (
                f"The wallet '{debtor_wallet.id}' of '{debtor_wallet.user.id}' "
                f"has not enough funds for a charge of {debtor_amount_to_charge} {ValidCurrencies.attributes[debtor_wallet.currency]}"
            )
            logger.warning(message)
            raise InsufficientFundsException(message)
        logger.info(
            f"The commerce '{creditor_wallet.user.id}' will charge "
            f"{debtor_amount_to_charge} {ValidCurrencies.attributes[debtor_wallet.currency]}"
        )

        # Transfer the funds and create the action
        creditor_wallet.balance += creditor_amount_to_charge
        creditor_wallet.save()
        Action(
            created_by=creditor_wallet.user,
            created=timezone.now(),
            wallet=creditor_wallet,
            action_type=ValidActions.payment,
            comment=comment,
            delta=creditor_amount_to_charge
        ).save()

        # Charge the amount to the debtor funds
        debtor_wallet.balance -= debtor_amount_to_charge
        debtor_wallet.save()
        Action(
            created_by=creditor_wallet.user,
            created=timezone.now(),
            wallet=debtor_wallet,
            action_type=ValidActions.charge,
            comment=comment,
            delta=-debtor_amount_to_charge
        ).save()

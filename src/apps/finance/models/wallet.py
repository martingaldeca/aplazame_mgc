from django.db import models
from logging import getLogger
from django.contrib.auth.models import User
from djchoices import DjangoChoices, ChoiceItem
import uuid  # Use to generate secure and unique tokens

logger = getLogger(__name__)


class ValidCurrencies(DjangoChoices):
    """
    Allowed user types for users in the platform
    """
    EUR = ChoiceItem(0)
    USD = ChoiceItem(1)


class Wallet(models.Model):
    """
    Model for wallet of an user
    """
    class Meta:
        verbose_name = 'User wallet'

    user = models.ForeignKey(User, on_delete=models.PROTECT, db_index=True)  # One user can have many wallets but all wallets must have only one user
    token = models.UUIDField(default=uuid.uuid1, editable=False, null=False, blank=False, db_index=True)
    name = models.CharField(max_length=128, verbose_name="Wallet name", default="Wallet", blank=True, null=True)
    description = models.CharField(max_length=300, verbose_name="Wallet description", default="", blank=True, null=True)
    balance = models.DecimalField(default=0, verbose_name="Wallet funds", blank=False, null=False, max_digits=50, decimal_places=8)
    currency = models.IntegerField(
        choices=ValidCurrencies.choices, default=ValidCurrencies.EUR, null=True, blank=True, verbose_name="Wallet currency"
    )

    def __str__(self):
        return f'{self.user.id}-{self.balance}-{ValidCurrencies.attributes[self.currency]}s-{self.token}'



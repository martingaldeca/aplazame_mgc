from django.db import models
from logging import getLogger
from django.contrib.auth.models import User


from djchoices import DjangoChoices, ChoiceItem

from apps.finance.models import Wallet

logger = getLogger(__name__)


class ValidActions(DjangoChoices):
    """
    Allowed user types for users in the platform
    """
    deposit = ChoiceItem(0)
    charge = ChoiceItem(1)
    withdraw = ChoiceItem(2)
    payment = ChoiceItem(3)


class Action(models.Model):
    class Meta:
        verbose_name = 'Wallet Action'

    created_by = models.ForeignKey(User, on_delete=models.PROTECT, help_text='User who performed the action.', db_index=True)
    created = models.DateTimeField(blank=True, db_index=True)
    wallet = models.ForeignKey(Wallet, db_index=True, on_delete=models.PROTECT)
    action_type = models.IntegerField(choices=ValidActions.choices, default=ValidActions.deposit, null=True, blank=True)
    comment = models.TextField(blank=True, help_text="Comment of the action.")
    delta = models.DecimalField(default=0, blank=False, null=False, max_digits=50, decimal_places=8)

    def __str__(self):
        return (
            f"Action for wallet {self.wallet.id} created by {self.created_by.id} at {self.created}. "
            f"[Delta = {self.delta} - {ValidActions.attributes[self.action_type]}]"
        )
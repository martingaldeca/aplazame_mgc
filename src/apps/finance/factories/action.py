import factory

from django.utils import timezone

from apps.finance.models import Action, ValidActions
from apps.core.factories import UserFactory
from apps.finance.factories import WalletFactory


class ActionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Action
        django_get_or_create = ('created_by', 'wallet')

    created_by = factory.SubFactory(UserFactory)
    created = timezone.now()
    wallet = factory.SubFactory(WalletFactory)
    action_type = ValidActions.deposit
    comment = 'Test deposit'
    delta = 0.0

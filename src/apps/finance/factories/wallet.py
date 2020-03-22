import factory
import uuid
import random

from apps.finance.models import Wallet, ValidCurrencies
from apps.core.factories import UserFactory


class WalletFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Wallet
        django_get_or_create = ('user',)

    user = factory.SubFactory(UserFactory)
    token = uuid.uuid1()
    name = 'Wallet name'
    description = 'Wallet description'
    balance = random.uniform(0, 10000000)
    currency = ValidCurrencies.EUR

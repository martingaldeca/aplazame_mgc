import factory

from apps.core.models import UserProfile, UserTypes
from apps.core.factories import UserFactory


class UserProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UserProfile
        django_get_or_create = ('user',)

    user = factory.SubFactory(UserFactory)
    user_type = UserTypes.customer

import factory
from django.contrib.auth.models import User


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Faker('name')
    first_name = 'Fake'
    last_name = 'FakeLast'
    email = 'pruebas@pruebas.com'
    is_staff = False
    is_active = True
    is_superuser = False

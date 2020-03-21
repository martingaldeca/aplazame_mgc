import logging

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from apps.core.factories import UserFactory

logger = logging.getLogger(__name__)


def resolve_user(username: str, user__first_name: str = None, user__last_name: str = None, user__email: str = None) -> User:
    """
    Check if the user exists, if not create a new one
    :param user__email:
    :param user__last_name:
    :param user__first_name:
    :param username:
    :return:
    """
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        # Check if username param is str, useful to avoid database crash
        if type(username) is not str:
            raise ValidationError(f"username param should be '{str}' instead of '{type(username)}'.")

        logger.info(f"The user '{username}' does not exists. A new user will be created.")
        user = UserFactory(
            username=username,
            first_name=user__first_name if user__first_name is not None else '',
            last_name=user__last_name if user__last_name is not None else '',
            email=user__email if user__email is not None else ''
        )

    return user

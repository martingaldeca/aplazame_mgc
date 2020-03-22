import logging

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from apps.core.factories import UserProfileFactory
from apps.core.models import UserProfile
from apps.core.resolvers import resolve_user

logger = logging.getLogger(__name__)


def resolve_user_profile(user__username: str, user_type: int = 1) -> UserProfile:
    """
    Check if the user profile exists, if not create a fake one
    :param user__username:
    :param user_type:
    :return:
    """
    try:
        user_profile = UserProfile.objects.get(user__username=user__username)
    except UserProfile.DoesNotExist:
        # Check if username param is str, useful to avoid database crash
        if type(user__username) is not str:
            raise ValidationError(f"username param should be '{str}' instead of '{type(user__username)}'.")
        if type(user_type) is not int:
            raise ValidationError(f"user_type param should be '{int}' instead of '{type(user_type)}'.")

        logger.debug(f"The user profile for user '{user__username}' does not exists. A new user profile will be created.")
        user = resolve_user(username=user__username)
        user_profile = UserProfileFactory(
            user=user,
            user_type=user_type
        )

    return user_profile

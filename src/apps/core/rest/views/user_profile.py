import logging

from apps.core.helpers.generic_list import GenericList
from apps.core.rest.serializers import UserProfileSerializer
from apps.core.models import UserProfile

from apps.core.resolvers import resolve_user

logger = logging.getLogger(__name__)


class UserProfileList(GenericList):
    """
    List and create User Profiles
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.serializer_class = UserProfileSerializer
        self.model = UserProfile

        self.deep_fields = ['user__username', 'user__id', 'user__email']
        self.fields_to_resolve = {
            'user': {
                'resolver': resolve_user,
                'extra_parameters': ['user__first_name', 'user__last_name', 'user__email']
            }
        }
        self.identification_value = 'user'



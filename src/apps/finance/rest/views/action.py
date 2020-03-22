import logging

from apps.core.helpers.generic_list import GenericList
from apps.finance.rest.serializers import ActionSerializer
from apps.finance.models import Action

logger = logging.getLogger(__name__)


class ActionList(GenericList):
    """
    List and create User Profiles
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.serializer_class = ActionSerializer
        self.model = Action

        self.deep_fields = ['created_by__username', 'created_by__id', 'created_by__email']
        self.identification_value = 'id'

        # You can not directly post to Wallet model for obviously reasons
        self.post_allowed = False


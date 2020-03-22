import logging

from apps.core.helpers.generic_list import GenericList
from apps.finance.rest.serializers import WalletSerializer
from apps.finance.models import Wallet

logger = logging.getLogger(__name__)


class WalletList(GenericList):
    """
    List and create User Profiles
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.serializer_class = WalletSerializer
        self.model = Wallet

        self.deep_fields = ['user__username', 'user__id', 'user__email']
        self.identification_value = 'id'

        # You can not directly post to Wallet model for obviously reasons
        self.post_allowed = False


from apps.finance.models import Wallet
from apps.core.rest.serializers import UserSerializer
from rest_framework import serializers


class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = [
            'id', 'user', 'token', 'name', 'description', 'balance', 'currency'
        ]

    def to_representation(self, instance):
        self.fields['user'] = UserSerializer(read_only=True)
        return super(WalletSerializer, self).to_representation(instance)

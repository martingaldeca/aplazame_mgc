from apps.finance.models import Action
from apps.finance.rest.serializers import WalletSerializer
from apps.core.rest.serializers import UserSerializer
from rest_framework import serializers


class ActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Action
        fields = [
            'id', 'created_by', 'created', 'wallet', 'action_type', 'comment', 'delta'
        ]

    def to_representation(self, instance):
        self.fields['created_by'] = UserSerializer(read_only=True)
        self.fields['wallet'] = WalletSerializer(read_only=True)
        return super(ActionSerializer, self).to_representation(instance)

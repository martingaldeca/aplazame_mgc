from apps.core.models import UserProfile
from apps.core.rest.serializers import UserSerializer
from rest_framework import serializers


class UserProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserProfile
        fields = [
            'id', 'user', 'user_type'
        ]

    def to_representation(self, instance):
        self.fields['user'] = UserSerializer(read_only=True)
        return super(UserProfileSerializer, self).to_representation(instance)
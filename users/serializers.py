from django.utils.crypto import get_random_string
from rest_framework import serializers
from django.contrib.auth.models import User

from .models import UserProfile


class ManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name']


class UserProfileSerializer(serializers.ModelSerializer):
    user_id = serializers.ReadOnlyField(source='user.id')

    class Meta:
        model = UserProfile
        fields = ['user_id', 'first_name', 'last_name']


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(source='userprofile', required=False)

    class Meta:
        model = User
        fields = ['email', 'is_staff', 'is_active', 'profile']

    def create(self, validated_data):
        profile_data = validated_data.pop('userprofile', {})

        username = get_random_string(10)
        while User.objects.filter(username=username).exists():
            username = get_random_string(10)

        user = User.objects.create(username=username, **validated_data)

        if not UserProfile.objects.filter(user=user).exists():
            UserProfile.objects.create(
                user=user,
                role='manager',
                first_name=profile_data.get('first_name', ''),
                last_name=profile_data.get('last_name', '')
            )

        return user

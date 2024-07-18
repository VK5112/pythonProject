from rest_framework import serializers
from django.contrib.auth.models import User
from .models import OrderModel, UserProfile


class UserSerializer(serializers.ModelSerializer):
    role = serializers.CharField(source='userprofile.role')

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'role')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        profile_data = validated_data.pop('userprofile', {})
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        UserProfile.objects.create(user=user, **profile_data)
        return user


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderModel
        fields = '__all__'

import re

from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.translation import gettext_lazy as _


class CustomTokenObtainPairSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                raise serializers.ValidationError(_('No account found with this email address.'))

            if not user.check_password(password):
                raise serializers.ValidationError(_('Incorrect password.'))

            data = {}
            refresh = RefreshToken.for_user(user)
            data['refresh'] = str(refresh)
            data['access'] = str(refresh.access_token)

            data.update({
                'user_id': user.id,
                'username': user.username,
                'role': user.userprofile.role,
                'first_name': user.first_name,
                'last_name': user.last_name,
            })

            return data
        else:
            raise serializers.ValidationError(_('Must include "email" and "password".'))




class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField(required=True, help_text="Refresh token")

    def validate(self, attrs):
        refresh = attrs.get("refresh")
        if not refresh:
            raise serializers.ValidationError("Refresh token is required.")
        return attrs


class ActivateUserSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True, required=True)

    @staticmethod
    def validate_password(value):
        password_pattern = r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&^#])[A-Za-z\d@$!%*?&^#]{8,}$'

        if not re.match(password_pattern, value):
            raise serializers.ValidationError(
                _(
                    "Password must contain at least 8 characters, including at least one uppercase letter,"
                    "one lowercase letter, one number, and one special character (@$!%*?&^#)."
                )
            )
        return value

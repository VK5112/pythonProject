from django.contrib.auth.models import User
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken


def activate_user_service(token, password):
    refresh_token = RefreshToken(token)
    user_id = refresh_token.get('user_id')

    if not user_id:
        raise serializers.ValidationError("Invalid token")

    user = User.objects.get(id=user_id)

    if user.is_active:
        raise serializers.ValidationError("User is already active")

    user.set_password(password)
    user.is_active = True
    user.save()


def blacklist_token_service(refresh_token):
    try:
        token = RefreshToken(refresh_token)
        token.blacklist()
    except Exception as e:
        raise ValidationError("Invalid token or token is already blacklisted.")


def handle_activate_user(token, password):
    try:
        activate_user_service(token, password)
        return Response({"detail": "User activated successfully"}, status=status.HTTP_200_OK)
    except serializers.ValidationError as e:
        return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
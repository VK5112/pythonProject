from django.utils.crypto import get_random_string
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile, OrderModel, Comment, Group
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.translation import gettext_lazy as _

STATUS_CHOICES = ['In work', 'New', 'Agree', 'Disagree', 'Dubbing']
COURSE_CHOICES = ['FS', 'QACX', 'JCX', 'JSCX', 'FE', 'PCX']
COURSE_TYPE_CHOICES = ['pro', 'minimal', 'premium', 'incubator', 'vip']
COURSE_FORMAT_CHOICES = ['static', 'online']


class ManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name']


class CommentSerializer(serializers.ModelSerializer):
    first_name = serializers.ReadOnlyField(source='user.first_name')
    last_name = serializers.ReadOnlyField(source='user.last_name')

    class Meta:
        model = Comment
        fields = ['id', 'first_name', 'last_name', 'text', 'created_at', 'order']


class OrderSerializer(serializers.ModelSerializer):
    manager = serializers.CharField(source='manager.first_name', read_only=True)

    class Meta:
        model = OrderModel
        fields = [
            'id', 'name', 'surname', 'email', 'phone', 'age', 'course', 'course_format',
            'course_type', 'sum', 'alreadyPaid', 'created_at', 'status', 'group', 'manager'
        ]
        read_only_fields = ['comments']

    def create(self, validated_data):
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data = {k: v for k, v in validated_data.items() if v != ""}
        return super().update(instance, validated_data)

    @staticmethod
    def validate_status(value):
        if value and value not in STATUS_CHOICES:
            raise serializers.ValidationError(f'Status must be one of {STATUS_CHOICES}')
        return value

    @staticmethod
    def validate_course(value):
        if value and value not in COURSE_CHOICES:
            raise serializers.ValidationError(f'Course must be one of {COURSE_CHOICES}')
        return value

    @staticmethod
    def validate_course_format(value):
        if value and value not in COURSE_FORMAT_CHOICES:
            raise serializers.ValidationError(f'Course format must be one of {COURSE_FORMAT_CHOICES}')
        return value

    @staticmethod
    def validate_course_type(value):
        if value and value not in COURSE_TYPE_CHOICES:
            raise serializers.ValidationError(f'Course type must be one of {COURSE_TYPE_CHOICES}')
        return value


class UserProfileSerializer(serializers.ModelSerializer):
    user_id = serializers.ReadOnlyField(source='user.id')

    class Meta:
        model = UserProfile
        fields = ['user_id', 'first_name', 'last_name']


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(source='userprofile', required=False)

    class Meta:
        model = User
        fields = ['email', 'is_staff', 'profile']

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


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name']

    @staticmethod
    def validate_name(value):
        if Group.objects.filter(name=value).exists():
            raise serializers.ValidationError("Group with this name already exists.")
        return value


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, attrs):
        refresh = attrs.get("refresh")
        if not refresh:
            raise serializers.ValidationError("Refresh token is required.")
        return attrs


class ActivateUserSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True, required=True)

    @staticmethod
    def validate_password(value):
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        return value

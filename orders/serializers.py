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
    utm = serializers.ReadOnlyField(source='order.utm')
    msg = serializers.ReadOnlyField(source='order.msg')

    class Meta:
        model = Comment
        fields = ['id', 'first_name', 'last_name', 'text', 'created_at', 'order', 'utm', 'msg']


class OrderSerializer(serializers.ModelSerializer):
    manager = ManagerSerializer(read_only=True)

    class Meta:
        model = OrderModel
        fields = [
            'id', 'name', 'surname', 'email', 'phone', 'age', 'course', 'course_format',
            'course_type', 'sum', 'alreadyPaid', 'created_at', 'status', 'group', 'manager'
        ]
        read_only_fields = ['comments']

    def create(self, validated_data):
        manager_username = validated_data.pop('manager', None)
        if manager_username:
            validated_data['manager'] = User.objects.get(username=manager_username.username)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        manager_username = validated_data.pop('manager', None)
        validated_data = {k: v for k, v in validated_data.items() if v != ""}
        if manager_username:
            validated_data['manager'] = User.objects.get(username=manager_username.username)
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


class UserSerializer(serializers.ModelSerializer):
    email = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = {'id', 'username', 'password', 'email', 'first_name', 'last_name', 'is_active', 'is_superuser',
                  'is_staff', 'date_joined', 'last_login'}
        extra_kwargs = {'password': {'write_only': True}}

    @staticmethod
    def get_email(obj):
        if obj.is_superuser:
            return '********'
        return obj.email

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        UserProfile.objects.update_or_create(
            user=user,
            defaults={
                'role': 'manager',
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name
            }
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

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile, OrderModel, Comment
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

STATUS_CHOICES = ['In work', 'New', 'Aggre', 'Disaggre', 'Dubbing']
COURSE_CHOICES = ['FS', 'QACX', 'JCX', 'JSCX', 'FE', 'PCX']
COURSE_TYPE_CHOICES = ['pro', 'minimal', 'premium', 'incubator', 'vip']
COURSE_FORMAT_CHOICES = ['static', 'online']


class CommentSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Comment
        fields = ['id', 'user', 'text', 'created_at', 'order']


class OrderSerializer(serializers.ModelSerializer):
    manager_username = serializers.CharField(source='manager.username', read_only=True)
    manager = serializers.SlugRelatedField(slug_field='username', queryset=User.objects.all(), write_only=True,
                                           allow_null=True, required=False)
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = OrderModel
        fields = '__all__'

    def create(self, validated_data):
        manager_username = validated_data.pop('manager', None)
        if manager_username:
            validated_data['manager_username'] = manager_username.username
        return super().create(validated_data)

    def update(self, instance, validated_data):
        manager_username = validated_data.pop('manager', None)
        if manager_username:
            validated_data['manager_username'] = manager_username.username
            instance.manager = User.objects.get(username=manager_username.username)
        return super().update(instance, validated_data)

    @staticmethod
    def validate_status(value):
        if value and value not in STATUS_CHOICES:
            raise serializers.ValidationError(f'Status must be one of {STATUS_CHOICES}')
        return value

    @staticmethod
    def validate_course(value):
        if value not in COURSE_CHOICES:
            raise serializers.ValidationError(f'Course must be one of {COURSE_CHOICES}')
        return value

    @staticmethod
    def validate_course_format(value):
        if value not in COURSE_FORMAT_CHOICES:
            raise serializers.ValidationError(f'Course format must be one of {COURSE_FORMAT_CHOICES}')
        return value

    @staticmethod
    def validate_course_type(value):
        if value not in COURSE_TYPE_CHOICES:
            raise serializers.ValidationError(f'Course type must be one of {COURSE_TYPE_CHOICES}')
        return value


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'email', 'first_name', 'last_name']
        extra_kwargs = {'password': {'write_only': True}}

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


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token['user_id'] = user.id
        token['username'] = user.username

        user_profile = UserProfile.objects.get(user=user)
        token['role'] = user_profile.role
        token['first_name'] = user_profile.first_name
        token['last_name'] = user_profile.last_name

        return token

    def validate(self, attrs):
        data = super().validate(attrs)

        user_data = {
            'user_id': self.user.id,
            'username': self.user.username,
            'role': self.user.userprofile.role,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
        }

        data.update(user_data)
        access = data.pop('access')
        refresh = data.pop('refresh')
        data['access'] = access
        data['refresh'] = refresh

        return data

from rest_framework import serializers
from .models import OrderModel


STATUS_CHOICES = ['In work', 'New', 'Agree', 'Disagree', 'Dubbing']
COURSE_CHOICES = ['FS', 'QACX', 'JCX', 'JSCX', 'FE', 'PCX']
COURSE_TYPE_CHOICES = ['pro', 'minimal', 'premium', 'incubator', 'vip']
COURSE_FORMAT_CHOICES = ['static', 'online']


class OrderSerializer(serializers.ModelSerializer):
    manager = serializers.CharField(source='manager.first_name', read_only=True)

    class Meta:
        model = OrderModel
        fields = [
            'id', 'name', 'surname', 'email', 'phone', 'age', 'course', 'course_format',
            'course_type', 'sum', 'alreadyPaid', 'created_at', 'updated_at', 'status', 'group', 'manager'
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


class EmptySerializer(serializers.Serializer):
    pass

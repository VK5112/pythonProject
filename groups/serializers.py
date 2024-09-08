from rest_framework import serializers

from .models import Group


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name']

    @staticmethod
    def validate_name(value):
        if Group.objects.filter(name=value).exists():
            raise serializers.ValidationError("Group with this name already exists.")
        return value

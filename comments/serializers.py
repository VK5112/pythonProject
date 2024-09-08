from rest_framework import serializers

from .models import Comment


class CommentSerializer(serializers.ModelSerializer):
    first_name = serializers.ReadOnlyField(source='user.first_name')
    last_name = serializers.ReadOnlyField(source='user.last_name')

    class Meta:
        model = Comment
        fields = ['id', 'first_name', 'last_name', 'text', 'created_at', 'order']

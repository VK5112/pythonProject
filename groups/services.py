from rest_framework import status
from rest_framework.response import Response

from .models import Group


def create_group_service(group_data):
    group = Group.objects.create(**group_data)
    return group


def get_group_list_service():
    return Group.objects.all()


def handle_perform_create_group(serializer):
    group = create_group_service(serializer.validated_data)
    serializer.instance = group
    return Response(serializer.data, status=status.HTTP_201_CREATED)

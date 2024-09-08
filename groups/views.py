from rest_framework import generics, permissions, status
from rest_framework.response import Response

from .services import handle_perform_create_group
from .serializers import GroupSerializer
from .services import get_group_list_service


class GroupCreateView(generics.CreateAPIView):
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        return handle_perform_create_group(serializer)


class GroupListView(generics.ListAPIView):
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return get_group_list_service()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

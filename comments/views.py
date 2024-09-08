from rest_framework import generics, permissions

from .serializers import CommentSerializer
from .services import handle_create_comment, get_comment_list_service, handle_list_comments


class CommentCreateView(generics.CreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        return handle_create_comment(serializer, self.request.user)


class CommentListView(generics.ListAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return get_comment_list_service(self.kwargs['order_id'])

    def list(self, request, *args, **kwargs):
        return handle_list_comments(self.kwargs['order_id'], self.get_serializer_class())

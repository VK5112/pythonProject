from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView

from orders.permissions import IsAdminUserRole
from .serializers import UserSerializer
from .services import get_users_service, create_user_service


class UserListView(APIView):
    permission_classes = [IsAdminUserRole]

    @staticmethod
    def get(request):
        users = get_users_service()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class CreateUserView(generics.CreateAPIView):
    permission_classes = [IsAdminUserRole]
    serializer_class = UserSerializer
    def perform_create(self, serializer):
        user = create_user_service(self.request.data)
        serializer.instance = user
        return Response(serializer.data, status=status.HTTP_201_CREATED)

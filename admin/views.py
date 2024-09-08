from rest_framework import status, serializers
from rest_framework.response import Response
from rest_framework.views import APIView

from .services import get_order_statistics_service, get_user_order_statistics_service, ban_user_service, \
    unban_user_service, handle_generate_token_or_error
from orders.permissions import IsAdminUserRole


class OrderStatisticsView(APIView):
    permission_classes = [IsAdminUserRole]

    @staticmethod
    def get(request):
        result = get_order_statistics_service()
        return Response(result, status=status.HTTP_200_OK)


class UserOrderStatisticsView(APIView):
    permission_classes = [IsAdminUserRole]

    @staticmethod
    def get(request, id):
        result = get_user_order_statistics_service(id)
        return Response(result, status=status.HTTP_200_OK)

class BanUserView(APIView):
    permission_classes = [IsAdminUserRole]

    @staticmethod
    def patch(request, id):
        try:
            return ban_user_service(id)
        except serializers.ValidationError as e:
            return Response({'detail': str(e)}, status=status.HTTP_404_NOT_FOUND)


class UnbanUserView(APIView):
    permission_classes = [IsAdminUserRole]

    @staticmethod
    def patch(request, id):
        try:
            return unban_user_service(id)
        except serializers.ValidationError as e:
            return Response({'detail': str(e)}, status=status.HTTP_404_NOT_FOUND)


class UserActivationTokenView(APIView):
    permission_classes = [IsAdminUserRole]

    @staticmethod
    def get(request, id, *args, **kwargs):
        return handle_generate_token_or_error(id)

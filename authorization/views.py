import logging

from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .serializers import CustomTokenObtainPairSerializer, LogoutSerializer, ActivateUserSerializer
from .services import blacklist_token_service, handle_activate_user


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = LogoutSerializer

    @swagger_auto_schema(
        request_body=LogoutSerializer,
        responses={205: 'Logout successful', 400: 'Bad request'}
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        blacklist_token_service(serializer.validated_data["refresh"])
        return Response(status=status.HTTP_205_RESET_CONTENT)


logger = logging.getLogger(__name__)


class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.data.get("refresh")

        response = super().post(request, *args, **kwargs)

        try:
            refresh_token_instance = RefreshToken(refresh_token)
            refresh_token_instance.blacklist()
        except Exception as e:
            logger.error(f"Failed to blacklist token: {str(e)}")

        return response


class ActivateUserView(APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = ActivateUserSerializer

    @swagger_auto_schema(request_body=ActivateUserSerializer)
    def post(self, request, token, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return handle_activate_user(token, serializer.validated_data["password"])

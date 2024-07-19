from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import UserProfile, OrderModel, Comment
from .serializers import UserSerializer, OrderSerializer, CustomTokenObtainPairSerializer, CommentSerializer
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import OrderingFilter

class CommentCreateView(generics.CreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        order = serializer.validated_data['order']
        if order.manager is None or order.manager == self.request.user:
            order.manager = self.request.user
            if order.status in [None, 'New']:
                order.status = 'In Work'
            order.save()
            serializer.save(user=self.request.user)
        else:
            raise serializers.ValidationError('You cannot comment on this order.')

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        UserProfile.objects.update_or_create(
            user=user,
            defaults={
                'role': 'manager',
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name
            }
        )

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class OrderPagination(PageNumberPagination):
    page_size = 25

class OrderModelViewSet(ModelViewSet):
    queryset = OrderModel.objects.all().order_by('-id')
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = OrderPagination
    filter_backends = [OrderingFilter]
    ordering_fields = '__all__'
    ordering = ['-id']

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
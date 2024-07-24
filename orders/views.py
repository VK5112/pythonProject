from rest_framework import generics, permissions, status, serializers
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import UserProfile, OrderModel, Comment, Group, STATUS_CHOICES
from .serializers import UserSerializer, OrderSerializer, CustomTokenObtainPairSerializer, CommentSerializer, \
    GroupSerializer
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import OrderingFilter
from rest_framework.generics import ListAPIView
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from .filters import OrderFilter
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.db import models
from rest_framework.permissions import IsAdminUser


class IsOrderManagerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.manager is None or obj.manager == request.user


class CommentCreateView(generics.CreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        order = serializer.validated_data['order']
        if order.manager is None or order.manager == self.request.user:
            order.manager = self.request.user
            if order.status not in STATUS_CHOICES or order.status in [None, 'New']:
                order.status = 'In work'
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
    permission_classes = [permissions.IsAuthenticated, IsOrderManagerOrReadOnly]
    pagination_class = OrderPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = OrderFilter
    ordering_fields = '__all__'
    ordering = ['-id']

    @action(detail=False, methods=['post'], url_path='filter', url_name='filter-orders')
    def filter_orders(self, request):
        filter_data = {k: v for k, v in request.data.items() if v}
        filtered_orders = OrderModel.objects.filter(**filter_data)
        page = self.paginate_queryset(filtered_orders)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(filtered_orders, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def add_group(self, request, pk=None):
        order = self.get_object()
        group = request.data.get('group')
        if group:
            order.group = group
            order.save()
            return Response({'status': 'group added'})
        return Response({'error': 'Group not provided'}, status=status.HTTP_400_BAD_REQUEST)

    def perform_update(self, serializer):
        serializer.save(manager=self.request.user)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        validated_data = {k: v for k, v in serializer.validated_data.items() if v != ""}
        if 'manager' in validated_data:
            validated_data.pop('manager')
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.manager = self.request.user
        instance.save()

        return Response(serializer.data)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class CommentListView(ListAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        order_id = self.kwargs['order_id']
        return Comment.objects.filter(order_id=order_id).order_by('-created_at')


class GroupCreateView(generics.CreateAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]


class GroupListView(generics.ListAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]


class LogoutView(APIView):
    @staticmethod
    def post(request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class OrderStatisticsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        total_count = OrderModel.objects.count()
        statuses = OrderModel.objects.values('status').annotate(count=models.Count('status'))

        null_count = OrderModel.objects.filter(status__isnull=True).count()

        status_counts = {status['status']: status['count'] for status in statuses}
        status_counts[None] = null_count

        for status in ['In work', 'New', 'Agree', 'Disagree', 'Dubbing', None]:
            if status not in status_counts:
                status_counts[status] = 0

        sorted_statuses = sorted(status_counts.items(), key=lambda x: (x[0] is not None, str(x[0])))

        result = {
            'total_count': total_count,
            'statuses': [{'status': status if status is not None else 'null', 'count': count} for status, count in sorted_statuses]
        }

        return Response(result)

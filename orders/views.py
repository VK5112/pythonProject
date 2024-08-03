from django.db import models
from rest_framework import generics, permissions, status, serializers
from rest_framework.response import Response
from .models import OrderModel, Comment, Group, STATUS_CHOICES
from .serializers import OrderSerializer, CustomTokenObtainPairSerializer, CommentSerializer, GroupSerializer
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import OrderingFilter
from rest_framework.generics import ListAPIView
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from .filters import OrderFilter
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAdminUser
from django.contrib.auth.models import User


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


class OrderPagination(PageNumberPagination):
    page_size = 25


class OrderModelViewSet(ReadOnlyModelViewSet):
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

    @staticmethod
    def get(request):
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
            'statuses': [{'status': status if status is not None else 'null', 'count': count} for status, count in
                         sorted_statuses]
        }

        return Response(result)


# New code for listing users
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined', 'last_login']


class UserListView(APIView):
    permission_classes = [IsAdminUser]

    @staticmethod
    def get(request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

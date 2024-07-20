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
    filter_backends = [OrderingFilter]
    ordering_fields = '__all__'
    ordering = ['-id']

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
        serializer.instance.manager = self.request.user
        serializer.save()

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

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

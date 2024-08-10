from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, permissions, status, serializers
from rest_framework.response import Response
from .models import OrderModel, Comment, Group, STATUS_CHOICES
from .serializers import OrderSerializer, CustomTokenObtainPairSerializer, CommentSerializer, GroupSerializer, \
    UserSerializer, LogoutSerializer
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import RetrieveModelMixin, ListModelMixin
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import OrderingFilter
from rest_framework.generics import ListAPIView
from django_filters.rest_framework import DjangoFilterBackend
from .filters import OrderFilter
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAdminUser
from django.contrib.auth.models import User
from django.db.models import Count


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


class OrderModelViewSet(RetrieveModelMixin, ListModelMixin, GenericViewSet):
    queryset = OrderModel.objects.all().order_by('-id')
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrderManagerOrReadOnly]
    pagination_class = OrderPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = OrderFilter
    ordering_fields = '__all__'
    ordering = ['-id']

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)


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
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = LogoutSerializer

    @swagger_auto_schema(
        request_body=LogoutSerializer,
        responses={205: 'Token successfully blacklisted', 400: 'Bad Request'}
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            refresh_token = serializer.validated_data["refresh"]
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
        statuses = OrderModel.objects.values('status').annotate(count=Count('status'))

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


class UserOrderStatisticsView(APIView):
    permission_classes = [IsAdminUser]

    @staticmethod
    def get(request, id):
        user = User.objects.get(pk=id)
        orders = OrderModel.objects.filter(manager=user)

        statuses = orders.values('status').annotate(count=Count('status'))

        result = {
            'total_count': orders.count(),
            'statuses': [{'status': status['status'], 'count': status['count']} for status in statuses]
        }

        return Response(result)


class UserListView(APIView):
    permission_classes = [IsAdminUser]

    @staticmethod
    def get(request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)


class BanUserView(APIView):
    permission_classes = [IsAdminUser]

    @staticmethod
    def patch(request, id):
        try:
            user = User.objects.get(pk=id)
            user.is_active = False
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except User.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)


class UnbanUserView(APIView):
    permission_classes = [IsAdminUser]

    @staticmethod
    def patch(request, id):
        try:
            user = User.objects.get(pk=id)
            user.is_active = True
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except User.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

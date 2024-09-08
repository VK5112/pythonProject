from rest_framework import permissions, serializers
from rest_framework.generics import GenericAPIView
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import RetrieveModelMixin, ListModelMixin
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from .filters import OrderFilter
from .models import OrderModel
from .serializers import OrderSerializer
from .permissions import IsOrderManagerOrReadOnly
from .services import (
    handle_partial_update_order, export_orders_to_excel_service,
)


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
        instance = self.get_object()
        return handle_partial_update_order(instance, request.data)


class EmptySerializer(serializers.Serializer):
    pass


class OrderExcelExportView(GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = OrderFilter
    ordering_fields = '__all__'
    ordering = ['-id']

    def get_serializer_class(self):
        if getattr(self, 'swagger_fake_view', False):
            return EmptySerializer
        return None

    def get(self, request, *args, **kwargs):
        orders = self.filter_queryset(OrderModel.objects.all())
        response = export_orders_to_excel_service(orders)
        return response

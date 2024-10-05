from django.urls import path, include
from rest_framework.routers import DefaultRouter

from comments.views import CommentCreateView, CommentListView
from orders.views import OrderExcelExportView, OrderModelViewSet

router=DefaultRouter()

router.register(r'', OrderModelViewSet, basename='order')

urlpatterns = [
    path('comments/', CommentCreateView.as_view(), name='comment_create'),
    path('comments/<int:order_id>/', CommentListView.as_view(), name='order_comments'),
    path('excel/export/', OrderExcelExportView.as_view(), name='orders_excel_export'),
    path('', include(router.urls)),
    ]
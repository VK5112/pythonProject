from django.urls import path, include
from rest_framework.routers import DefaultRouter
from orders.views import (
    OrderModelViewSet, CustomTokenObtainPairView, CommentCreateView,
    CommentListView, GroupCreateView, GroupListView, LogoutView, OrderStatisticsView,
    UserListView, UserOrderStatisticsView
)
from rest_framework_simplejwt.views import TokenRefreshView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

router = DefaultRouter()
router.register(r'orders', OrderModelViewSet, basename='order')

schema_view = get_schema_view(
    openapi.Info(
        title="Your API",
        default_version='v1',
        description="API documentation",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@yourapi.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    authentication_classes=[],
)

urlpatterns = [
    path('auth/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/logout/', LogoutView.as_view(), name='token_blacklist'),
    path('orders/comments/', CommentCreateView.as_view(), name='comment_create'),
    path('orders/comments/<int:order_id>/', CommentListView.as_view(), name='order_comments'),
    path('groups/', GroupCreateView.as_view(), name='group_create'),
    path('groups/list/', GroupListView.as_view(), name='group_list'),
    path('', include(router.urls)),
    path('admin/users/', UserListView.as_view(), name='admin_users_list'),
    path('admin/statistic/orders/', OrderStatisticsView.as_view(), name='admin_order_statistics'),
    path('admin/statistic/users/<int:id>/', UserOrderStatisticsView.as_view(), name='admin_user_order_statistics'),
    path('api/v1/doc/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]

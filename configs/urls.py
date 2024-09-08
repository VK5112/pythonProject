from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

from admin.views import BanUserView, UnbanUserView, OrderStatisticsView, UserOrderStatisticsView, \
    UserActivationTokenView
from auth.views import CustomTokenObtainPairView, LogoutView, ActivateUserView
from comments.views import CommentCreateView, CommentListView
from groups.views import GroupCreateView, GroupListView
from orders.views import OrderModelViewSet, OrderExcelExportView
from users.views import CreateUserView, UserListView

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
    path('orders/excel/', OrderExcelExportView.as_view(), name='orders_excel_export'),
    path('groups/', GroupCreateView.as_view(), name='group_create'),
    path('groups/list/', GroupListView.as_view(), name='group_list'),
    path('', include(router.urls)),
    path('admin/users', CreateUserView.as_view(), name='admin_users_create'),
    path('admin/users/', UserListView.as_view(), name='admin_users_list'),
    path('admin/users/<int:id>/ban/', BanUserView.as_view(), name='ban_user'),
    path('admin/users/<int:id>/unban/', UnbanUserView.as_view(), name='unban_user'),
    path('admin/statistic/orders/', OrderStatisticsView.as_view(), name='admin_order_statistics'),
    path('admin/statistic/users/<int:id>/', UserOrderStatisticsView.as_view(), name='admin_user_order_statistics'),
    path('admin/users/<int:id>/re_token/', UserActivationTokenView.as_view(), name='admin_users_re_token'),
    path('auth/activate/<str:token>', ActivateUserView.as_view(), name='auth_activate_create'),
    path('api/v1/doc/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]

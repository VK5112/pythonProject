from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from orders.views import OrderModelViewSet, RegisterView, CustomTokenObtainPairView, CommentCreateView, CommentListView, \
    GroupCreateView, GroupListView
from rest_framework_simplejwt.views import TokenRefreshView

router = DefaultRouter()
router.register(r'orders', OrderModelViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('register/', RegisterView.as_view(), name='register'),
    path('auth/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('comments/', CommentCreateView.as_view(), name='comment_create'),
    path('comments/<int:order_id>/', CommentListView.as_view(), name='order_comments'),
    path('groups/', GroupCreateView.as_view(), name='group_create'),
    path('groups/list/', GroupListView.as_view(), name='group_list'),
]

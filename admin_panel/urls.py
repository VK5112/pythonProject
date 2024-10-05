from django.urls import path

from admin_panel.views import BanUserView, UnbanUserView, OrderStatisticsView, UserOrderStatisticsView, \
    UserActivationTokenView
from users.views import CreateUserView, UserListView

urlpatterns = [
    path('users', CreateUserView.as_view(), name='admin_users_create'),
    path('users/', UserListView.as_view(), name='admin_users_list'),
    path('users/<int:id>/ban/', BanUserView.as_view(), name='ban_user'),
    path('users/<int:id>/unban/', UnbanUserView.as_view(), name='unban_user'),
    path('statistic/orders/', OrderStatisticsView.as_view(), name='admin_order_statistics'),
    path('statistic/users/<int:id>/', UserOrderStatisticsView.as_view(), name='admin_user_order_statistics'),
    path('users/<int:id>/re_token/', UserActivationTokenView.as_view(), name='admin_users_re_token'),
    ]
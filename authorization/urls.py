from django.urls import path

from authorization.views import CustomTokenObtainPairView, CustomTokenRefreshView, LogoutView, ActivateUserView

urlpatterns = [
    path('', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='token_blacklist'),
    path('activate/<str:token>', ActivateUserView.as_view(), name='auth_activate_create'),
    ]
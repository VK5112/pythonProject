from django.urls import path

from groups.views import GroupCreateView, GroupListView

urlpatterns = [
    path('', GroupCreateView.as_view(), name='group_create'),
    path('list/', GroupListView.as_view(), name='group_list'),
    ]
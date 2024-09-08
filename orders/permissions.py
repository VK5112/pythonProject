from rest_framework import permissions


class IsAdminUserRole(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.userprofile.role == 'admin'


class IsOrderManagerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if obj.manager is None or obj.manager == request.user:
            return True
        return False
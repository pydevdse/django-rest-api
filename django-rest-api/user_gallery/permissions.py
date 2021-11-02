from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS


class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user or request.method in SAFE_METHODS


class IsNotStaff(permissions.BasePermission):
    def has_permission(self, request, view):
        return not request.user.is_staff

# users/permissions.py

from rest_framework import permissions

class IsLibrarian(permissions.BasePermission):
    """
    Custom permission to only allow librarians to access certain views.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'librarian'

class IsMember(permissions.BasePermission):
    """
    Custom permission to only allow members to access certain views.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'member'

class IsAdminUser(permissions.BasePermission):
    """
    Custom permission to only allow admin users or superusers.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_superuser or 
            request.user.role == 'admin'
        )
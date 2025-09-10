from rest_framework import permissions


class IsTeacherOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow teachers or admins to access.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and (
            request.user.role in ['teacher', 'admin'] or
            request.user.is_staff or 
            request.user.is_superuser
        )

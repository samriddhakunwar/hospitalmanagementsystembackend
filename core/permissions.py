from rest_framework import permissions, viewsets
from rest_framework.response import Response
from rest_framework import status

class IsAdminOrReceptionist(permissions.BasePermission):
    """
    Custom permission to only allow admins or receptionists to modify objects.
    """
    def has_permission(self, request, view):
        # Allow read-only access for all authenticated users
        if request.method in permissions.SAFE_METHODS:
            return True
        # Allow write access for admins and receptionists
        return request.user.is_authenticated and (request.user.is_staff or request.user.role == 'receptionist')
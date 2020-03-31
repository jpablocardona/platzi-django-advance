"""Users permissions"""

# Django rest framework
from rest_framework.permissions import BasePermission

# Models
from cride.users.models import User


class IsAccountOwner(BasePermission):
    """Allow access only to objects owned by the requesting user"""

    def has_object_permission(self, request, view, obj):
        """Check object user"""
        return request.user == obj

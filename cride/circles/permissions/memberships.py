"""Circles permissions"""

# Django rest framework
from rest_framework.permissions import BasePermission

# Models
from cride.circles.models import Membership


class IsSelfMember(BasePermission):
    """Permissions"""

    def has_permission(self, request, view):
        obj = view.get_object()
        return self.has_object_permission(request, view, obj)

    def has_object_permission(self, request, view, obj):
        return request.user == obj.user


class IsActiveCircleMember(BasePermission):
    """Allow access only to circle member"""

    def has_permission(self, request, view):
        """Verify user have a membership in the object"""

        try:
            Membership.objects.get(
                user=request.user,
                circle=view.circle,
                is_active=True
            )
        except Membership.DoesNotExist:
            return False
        return True

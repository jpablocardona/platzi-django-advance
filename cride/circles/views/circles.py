"""Circles views"""

# Django rest frameworl
from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

# Filters
from rest_framework.filters import SearchFilter, OrderingFilter

# Model
from cride.circles.models import Circle

# Serialized
from cride.circles.serializers import CircleModelSerializer

# Permissions
from cride.circles.permissions import IsCircleAdmin


class CircleViewSet(mixins.CreateModelMixin,
                    mixins.RetrieveModelMixin,
                    mixins.UpdateModelMixin,
                    mixins.ListModelMixin,
                    viewsets.GenericViewSet):
    """Circle viewset"""

    serializer_class = CircleModelSerializer
    lookup_field = 'slug_name'

    # ordering = ('-members__count', '-rides_offered')

    # Filtros especiales
    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ('slug_name', 'name')
    ordering_fields = ('rides_offered', 'name', 'created')
    filter_fields = ('verified', 'is_limited')

    def get_queryset(self):
        queryset = Circle.objects.all()
        if self.action == 'list':
            return queryset.filter(is_public=True)
        return queryset

    def get_permissions(self):
        """Assing permission based on action"""
        permissions = [IsAuthenticated]
        if self.action in ['update', 'partial_update']:
            permissions.append(IsCircleAdmin)
        return [permision() for permision in permissions]

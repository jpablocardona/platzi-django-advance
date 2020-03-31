"""Users views"""

# Django Rest Framework
from rest_framework import status, viewsets, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

# Permissions
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated
)
from cride.users.permissions import IsAccountOwner

# Serializers
from cride.circles.serializers import CircleModelSerializer
from cride.users.serializers.profiles import ProfileModelSerializer
from cride.users.serializers.users import (
    UserLoginSerializer,
    UserSingUpSerializer,
    UserModelSerializer,
    UserVerifiedSerializer
)

# Models
from cride.users.models import User
from cride.circles.models import Circle


class UserViewSet(mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  viewsets.GenericViewSet):
    """User viewsets"""

    queryset = User.objects.filter(is_active=True, is_client=True)
    serializer_class = UserModelSerializer
    lookup_field = 'username'

    @action(detail=True, methods=['put', 'patch'])
    def profile(self, request, *args, **kwargs):
        """Update profile data"""
        user = self.get_object()
        profile = user.profile
        partial = request.method == 'PATCH'
        serializer = ProfileModelSerializer(
            profile,
            data=request.data,
            partial=partial
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        data = UserModelSerializer(user).data
        return Response(data)

    @action(detail=False, methods=['post'])
    def singup(self, request):
        """Handle HTTP POST request"""
        serialized = UserSingUpSerializer(data=request.data)
        serialized.is_valid(raise_exception=True)
        user = serialized.save()
        data = UserModelSerializer(user).data
        return Response(data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def login(self, request):
        """Handle HTTP POST request"""
        serialized = UserLoginSerializer(data=request.data)
        serialized.is_valid(raise_exception=True)
        user, token = serialized.save()
        data = {
            'status': 'ok',
            'user': UserModelSerializer(user).data,
            'token': token
        }
        return Response(data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def verified(self, request):
        """Handle HTTP POST request"""
        serialized = UserVerifiedSerializer(data=request.data)
        serialized.is_valid(raise_exception=True)
        serialized.save()
        data = {
            'message': 'Congratulations, now your share some rides'
        }
        return Response(data, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        """Add extra data to the response"""
        response = super(UserViewSet, self).retrieve(request, *args, **kwargs)
        circles = Circle.objects.filter(
            members=request.user,
            members__is_active=True
        )
        data = {
            'user': response.data,
            'circles': CircleModelSerializer(circles, many=True).data
        }
        response.data = data
        return response

    def get_permissions(self):
        """Assing permission based on action"""
        if self.action in ['singup', 'login', 'verified']:
            permissions = [AllowAny]
        elif self.action in ['retrieve', 'update', 'partial_update']:
            permissions = [IsAuthenticated, IsAccountOwner]
        else:
            permissions = [IsAuthenticated]
        return [permission() for permission in permissions]

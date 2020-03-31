"""Memberships model view"""

# Django rest framework
from rest_framework import viewsets, mixins, status
from rest_framework.generics import get_object_or_404
from rest_framework.decorators import action
from rest_framework.response import Response

# models
from cride.circles.models import Circle
from cride.circles.models import Membership

# serializers
from cride.circles.serializers import (
    MembershipModelSerializer,
    AddMemberSerializer
)

# permissions
from rest_framework.permissions import IsAuthenticated
from cride.circles.permissions import (
    IsActiveCircleMember,
    IsSelfMember
)
from cride.circles.models.invitations import Invitation


class MembershipViewSet(mixins.ListModelMixin,
                        mixins.CreateModelMixin,
                        mixins.DestroyModelMixin,
                        viewsets.GenericViewSet
                        ):
    """Class membership"""

    serializer_class = MembershipModelSerializer

    def get_permissions(self):
        permissions = [IsAuthenticated, IsActiveCircleMember]
        if self.action == 'invitations':
            permissions.append(IsSelfMember)
        return (p() for p in permissions)

    def dispatch(self, request, *args, **kwargs):
        """Verified that the circle exists"""

        slug_name = kwargs['slug_name']
        self.circle = get_object_or_404(Circle, slug_name=slug_name)
        return super(MembershipViewSet, self).dispatch(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = AddMemberSerializer(
            data=request.data,
            context={'circle': self.circle, 'request': request}
        )
        serializer.is_valid(raise_exception=True)
        member = serializer.save()

        data = self.get_serializer(member).data
        return Response(data, status=status.HTTP_201_CREATED)

    def get_queryset(self):
        """return circle members"""
        return Membership.objects.filter(
            circle=self.circle,
            is_active=True
        )

    def get_object(self):
        return get_object_or_404(
            Membership,
            user__username=self.kwargs['pk'],
            circle=self.circle,
            is_active=True
        )

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()

    @action(detail=True, methods=['POST'])
    def invitations(self, request, *args, **kwargs):
        member = self.get_object()

        invited_members = Membership.objects.filter(
            circle=self.circle,
            invited_by=request.user,
            is_active=True
        )

        unused_invitations = Invitation.objects.filter(
            circle=self.circle,
            issued_by=request.user,
            used=True
        ).values_list('code')
        diff = member.remaining_invitations - len(unused_invitations)

        invitations = [x[0] for x in unused_invitations]
        for i in range(0, diff):
            invitations.append(
                Invitation.objects.create(
                    issued_by=request.user,
                    circle=self.circle
                ).code
            )

        data = {
            'user_invitations': MembershipModelSerializer(invited_members, many=True).data,
            'invitations': invitations
        }
        return Response(data)

    @action(detail=True, methods=['POST'])
    def invitations(self, request, *args, **kwargs):
        pass

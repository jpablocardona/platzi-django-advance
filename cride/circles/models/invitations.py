"""Circles invitation model"""

# Django
from django.db import models

# Utilities
from cride.utils.models import CRideModel

# Managers
from cride.circles.managers import  InvitationManager


class Invitation(CRideModel):

    code = models.CharField(max_length=50, unique=True)
    issued_by = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='issue_by'
    )
    used_by = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        null=True
    )
    circle = models.ForeignKey('circles.Circle', on_delete=models.CASCADE)
    used = models.BooleanField(default=False)
    used_at = models.DateTimeField(blank=True, null=True)

    # Managers
    objects = InvitationManager()

    def __str__(self):
        return '#{}: {}'.format(self.circle.slug_name, self.code)


"""Profiles models"""

from django.db import models
from django.contrib.auth.models import AbstractUser

from cride.utils.models import CRideModel


class Profile(CRideModel):
    """Save de user advance data"""

    user = models.OneToOneField('users.User', models.CASCADE)

    picture = models.ImageField(
        'profile picture',
        upload_to='users/pictures/',
        blank=True,
        null=True
    )

    biography = models.TextField(max_length=500, blank=True)

    rides_taken = models.PositiveIntegerField(default=0)
    rides_offered = models.PositiveIntegerField(default=0)

    reputation = models.FloatField(
        default=5.0,
        help_text="User's reputation based on the rides taken and offered"
    )

    def __str__(self):
        """Return user's str representation"""
        return str(self.user)

"""Users models"""

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator

from cride.utils.models import CRideModel


class User(CRideModel, AbstractUser):
    """Extend from django abstract user change username field
    to email and add extra some fields"""

    email = models.EmailField(
        'email address',
        unique=True,
        error_messages={
            'unique': 'A email has register with other user'
        }
    )

    phone_regex = RegexValidator(
        regex=r'\+?1?\d{9,15}%',
        message='phone number must be entered in the format: +9999999. Up to 15 digits allowed'
    )
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    is_client = models.BooleanField(
        'client status',
        default=True,
        help_text=(
            'Help easily distinguish users and perform queries. '
            'Clients are the main type of user'
        )
    )

    is_verified = models.BooleanField(
        'verified',
        default=False,
        help_text='Set to true when the user have verified its email address'
    )

    def __str__(self):
        """ return username"""
        return self.username

    def __get_short_name__(self):
        """ return username"""
        return self.username

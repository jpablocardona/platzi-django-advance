""" django models utilities"""

from django.db import models


class CRideModel(models.Model):
    """ Comparte Ride base model

    CRideModel acts as an abstract base class from which every
    other model in the project will inherit. This class provides
    every table with the following attributes:

        + created (Datetime): Store the datetime to the object was created
        + updated (Datetime): Store the last datetime to the object was modified
    """

    created = models.DateTimeField(
        'created at',
        auto_now_add=True,
        help_text='Date time on which object was created'
    )

    modified = models.DateTimeField(
        'updated at',
        auto_now=True,
        help_text='Date time on which the object was last modified'
    )

    class Meta:
        """Meta options."""
        abstract = True

        get_latest_by = 'created'
        ordering = ['-created', '-modified']

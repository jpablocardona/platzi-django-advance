"""Circles models admin"""

# Django
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

# Models
from cride.circles.models import Circle


@admin.register(Circle)
class CircleAdmin(admin.ModelAdmin):
    """Circle model admin"""

    list_display = ('slug_name', 'verified', 'is_public', 'verified', 'is_limited', 'members_limited')
    search_fields = ('slug_name', 'name')
    list_filter = ('is_public', 'verified', 'is_limited')

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # list_display = ('email', 'first_name', 'last_name', 'is_staff'),
    search_fields = ("email",)

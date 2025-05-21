from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib import admin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('first_name', 'last_name', 'email', 'is_staff')

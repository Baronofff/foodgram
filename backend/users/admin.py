from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm as BaseUserCreationForm

from .models import User, Subscription


class RequiredFieldsUsersCreationForm(BaseUserCreationForm):
    """Форма для создания пользователя с проверкой на обязательные поля."""
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True, label="Name")
    last_name = forms.CharField(required=True, label="Last_name")

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    add_form = RequiredFieldsUsersCreationForm
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    search_fields = ("email", 'username')
    list_filter = ('is_superuser', 'is_staff')


@admin.register(Subscription)
class SubscriptionsAdmin(admin.ModelAdmin):
    list_display = ['user', 'following']

from django.contrib.auth.models import AbstractUser
from django.db import models

from api.constants import MAX_USER_FIRST_NAME, MAX_USER_LAST_NAME


class User(AbstractUser):
    "Модель пользователя."
    email = models.EmailField(
        'Email',
        unique=True,
        error_messages={'unique': 'The email has been already registered'}
    )
    first_name = models.CharField(
        'Name', max_length=MAX_USER_FIRST_NAME
    )
    last_name = models.CharField(
        'Last Name', max_length=MAX_USER_LAST_NAME
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        null=True,
        blank=True,
        verbose_name='Avatar'
    )
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    class Meta:
        ordering = ['id']
        verbose_name = 'User'
        verbose_name_plural = 'Users'

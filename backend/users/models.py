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
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        ordering = ['id']


class Subscription(models.Model):
    author = models.ForeignKey(
        User,
        related_name='subscribers',
        on_delete=models.CASCADE,
    )
    subscribers = models.ForeignKey(
        User,
        related_name='subscriptions',
        on_delete=models.CASCADE,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name='unique_pair_of_author_and_subscriber',
                fields=['author', 'subscribers'],
            ),
            models.CheckConstraint(
                name='subscription_for_yourself_is_not_allowed',
                check=~models.Q(author=models.F('subscribers')),
            )
        ]

    def __str__(self):
        return f'{self.subscribers} подписчик {self.author}'

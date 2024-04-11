from django.db import models
from django.contrib.auth.models import AbstractUser

from consts import (
    USERNAME_LENGTH, FIRST_NAME_LENGTH, LAST_NAME_LENGTH,
    EMAIL_LENGTH, CONFIRMATION_CODE_LENGTH
)


class User(AbstractUser):
    username = models.CharField(
        verbose_name='имя пользователя',
        max_length=USERNAME_LENGTH,
        unique=True,
    )
    first_name = models.CharField(
        'имя',
        max_length=FIRST_NAME_LENGTH,
        blank=True)
    last_name = models.CharField(
        'фамилия',
        max_length=LAST_NAME_LENGTH,
        blank=True)
    email = models.EmailField(
        'адрес электронной почты',
        max_length=EMAIL_LENGTH,
        unique=True,
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'email']

    class Meta:
        verbose_name = 'Пользователи'
        verbose_name_plural = 'пользователи'
        default_related_name = 'users'
        ordering = ('username',)



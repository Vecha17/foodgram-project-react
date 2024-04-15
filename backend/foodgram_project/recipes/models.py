from django.db import models
from django.contrib.auth.models import AbstractUser

from .consts import (
    USERNAME_LENGTH, FIRST_NAME_LENGTH,
    LAST_NAME_LENGTH, EMAIL_LENGTH
)


class User(AbstractUser):
    username = models.CharField(
        verbose_name='имя пользователя',
        max_length=USERNAME_LENGTH,
        unique=True,
    )
    first_name = models.CharField(
        'имя',
        max_length=FIRST_NAME_LENGTH
    )
    last_name = models.CharField(
        'фамилия',
        max_length=LAST_NAME_LENGTH,
    )
    email = models.EmailField(
        'адрес электронной почты',
        max_length=EMAIL_LENGTH,
        unique=True,
    )
    is_subscribed = models.BooleanField(default=False)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователи'
        verbose_name_plural = 'пользователи'
        default_related_name = 'users'
        ordering = ('username',)


class Follow(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='user'
    )
    following = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='following'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'following'],
                name='unique_user_following'
            )
        ]


class Tag(models.Model):
    name = models.CharField(max_length=50),
    color = models.CharField(max_length=50),
    slug = models.SlugField(max_length=50)

    class Meta:
        verbose_name = 'Тэги'
        verbose_name_plural = 'тэги'
        default_related_name = 'tags'


class Ingredient(models.Model):
    name = models.CharField(max_length=250)
    unit_of_measurement = models.CharField(max_length=50)


class Recipe(models.Model):
    tags = models.ManyToManyField(Tag)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор',
    )
    ingredients = models.ManyToManyField(Ingredient, through='Value')
    is_favorited = models.BooleanField()
    is_in_shopping_cart = models.BooleanField()
    name = models.CharField(max_length=200)
    image = models.ImageField()
    text = models.CharField(max_length=256)
    cooking_time = models.PositiveSmallIntegerField()


class Value(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    value = models.CharField

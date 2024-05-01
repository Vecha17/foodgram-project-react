from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator

from . import consts


class User(AbstractUser):
    username = models.CharField(
        verbose_name='имя пользователя',
        max_length=consts.USERNAME_LENGTH,
        unique=True,
    )
    first_name = models.CharField(
        'имя',
        max_length=consts.FIRST_NAME_LENGTH
    )
    last_name = models.CharField(
        'фамилия',
        max_length=consts.LAST_NAME_LENGTH,
    )
    email = models.EmailField(
        'адрес электронной почты',
        max_length=consts.EMAIL_LENGTH,
        unique=True,
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователи'
        verbose_name_plural = 'пользователи'
        default_related_name = 'users'
        ordering = ('username',)


class Subscription(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='subscriber'
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='subscribed'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_user_author'
            )
        ]
        verbose_name = 'Подписки'
        verbose_name_plural = 'подписки'
        default_related_name = 'subscripions'


class Tag(models.Model):
    GREEN = '#7CFC00'
    ORANGE = '#FF6347'
    PURPLE = '#8A2BE2'
    COLOR_TAG = [
        (GREEN, 'Зеленый'),
        (ORANGE, 'Оранжевый'),
        (PURPLE, 'Фиолетовый')
    ]
    name = models.CharField(
        max_length=consts.TAGS_CONSTS_LENGTH,
        unique=True
    ),
    color = models.CharField(
        max_length=consts.TAGS_CONSTS_LENGTH,
        choices=COLOR_TAG
    ),
    slug = models.SlugField(
        max_length=consts.TAGS_CONSTS_LENGTH,
        unique=True
    )

    class Meta:
        verbose_name = 'Тэги'
        verbose_name_plural = 'тэги'
        default_related_name = 'tags'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=consts.NAME_LENGTH)
    measurement_unit = models.CharField(max_length=consts.M_U_LENGTH)

    class Meta:
        verbose_name = 'Ингредиенты'
        verbose_name_plural = 'ингредиенты'
        default_related_name = 'ingredients'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Название тэга'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиент',
        through='Amount'
    )
    name = models.CharField(
        verbose_name='Название рецепта',
        max_length=consts.NAME_LENGTH
    )
    image = models.ImageField(
        verbose_name='Фото рецепта'
    )
    text = models.TextField(
        verbose_name='Описание рецепта',
        max_length=consts.TEXT_LENGTH
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        validators=[MinValueValidator(1, 'Минимальное время приготовления')],
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'author'],
                name='unique_recipe')]


class Amount(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    amount = models.PositiveSmallIntegerField()

    class Meta:
        verbose_name = 'Количество ингредиентов в рецепте'
        verbose_name_plural = 'Количество ингредиентов в рецепте'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_ingredients')]


class Favorite(models.Model):
    author = models.ForeignKey(
        User,
        related_name='favorite',
        on_delete=models.CASCADE,
        verbose_name='Автор рецепта'
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name='favorite',
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Избранные рецепты'
        verbose_name_plural = 'Избранные рецепты'
        constraints = [models.UniqueConstraint(
            fields=['author', 'recipe'],
            name='unique_favorite')]


class ShopCart(models.Model):
    user = models.ForeignKey(
        User,
        related_name='shop_cart',
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name='shop_cart',
        on_delete=models.CASCADE,
        verbose_name='Рецепт для готовки'
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'
        constraints = [models.UniqueConstraint(
            fields=['user', 'recipe'],
            name='unique_cart')]

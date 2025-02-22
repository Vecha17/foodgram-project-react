from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

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

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class Subscription(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='subscriber',
        help_text='Текущий пользователь'
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='subscribed',
        help_text='Подписаться на автора рецепта'
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

    def __str__(self):
        return f'{self.user.username} подписан на {self.author.username}'


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
        unique=True,
        help_text='Введите название тэга'
    )
    color = models.CharField(
        max_length=consts.TAGS_CONSTS_LENGTH,
        choices=COLOR_TAG,
        help_text='Выберите цвет тэга'
    )
    slug = models.SlugField(
        max_length=consts.TAGS_CONSTS_LENGTH,
        unique=True,
        help_text='Введите слаг тэга'
    )

    class Meta:
        verbose_name = 'Тэги'
        verbose_name_plural = 'тэги'
        default_related_name = 'tags'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        max_length=consts.NAME_LENGTH,
        help_text='Введите название ингредиента'
    )
    measurement_unit = models.CharField(
        max_length=consts.M_U_LENGTH,
        help_text='Укажите единицу измерения ингредиента'
    )

    class Meta:
        ordering = ['id']
        verbose_name = 'Ингредиенты'
        verbose_name_plural = 'ингредиенты'
        default_related_name = 'ingredients'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Название тэга',
        help_text='Тэг рецепта'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор',
        help_text='Автор рецепта'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиент',
        through='Amount',
    )
    name = models.CharField(
        verbose_name='Название рецепта',
        max_length=consts.NAME_LENGTH,
        help_text='Введите название рецепта'
    )
    image = models.ImageField(
        upload_to='static/images/',
        verbose_name='Фото рецепта',
        help_text='Добавьте фото рецепта'
    )
    text = models.TextField(
        verbose_name='Описание рецепта',
        max_length=consts.TEXT_LENGTH,
        help_text='Добавьте описание приготовления рецепта'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        validators=[
            MinValueValidator(
                consts.MIN_VALUE_VALID, 'Минимальное время приготовления'
            ),
            MaxValueValidator(
                consts.MAX_VALUE_VALID, 'Максимальное время приготовления'
            )
        ],
        help_text='Укажите время приготовления в минутах'
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'author'],
                name='unique_recipe')]

    def __str__(self):
        return self.name


class Amount(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
        help_text='Выберите рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='in_recipe',
        help_text='Выберите ингредиент'
    )
    amount = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(
                consts.MIN_VALUE_VALID, 'Минимальное количество ингредиента'
            ),
            MaxValueValidator(
                consts.MAX_VALUE_VALID, 'Максимальное количество ингредиента'
            )
        ],
        help_text='Введите количество ингредиента'
    )

    class Meta:
        verbose_name = 'Количество ингредиентов в рецепте'
        verbose_name_plural = 'Количество ингредиентов в рецепте'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_ingredients')]

    def __str__(self):
        return (
            f'{self.amount} {self.ingredient.measurement_unit} '
            f'{self.ingredient.name} в рецепте {self.recipe.name}'
        )


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

    def __str__(self):
        return f'{self.recipe.name} в избранном у {self.author.username}'


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

    def __str__(self):
        return f'{self.recipe.name} в списке покупок у {self.user.username}'

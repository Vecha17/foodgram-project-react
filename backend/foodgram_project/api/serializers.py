import base64

from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from rest_framework import serializers
import webcolors

from recipes.models import User, Recipe, Tag, Ingredient, Subscription, Favorite, ShopCart, Amount
from recipes import consts
from .mixins import ValidateUsernameMixin


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class Hex2NameColor(serializers.Field):

    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        try:
            data = webcolors.hex_to_name(data)
        except ValueError:
            raise serializers.ValidationError('Для этого цвета нет имени')
        return data


class Ingredients2RecipeSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )
    amount = serializers.IntegerField()

    class Meta:
        model = Amount
        fields = ('id', 'amount')


class Recipe2SubSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class UserSerializer(serializers.ModelSerializer, ValidateUsernameMixin):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username',
            'first_name', 'last_name', 'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if Subscription.objects.filter(user=user, author=obj):
            return True
        return False


class SubscriptionSerializer(serializers.ModelSerializer):
    email = serializers.ReadOnlyField(source='author.email')
    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count'
        )

    def get_is_subscribed(self, obj):
        if Subscription.objects.filter(user=obj.user, author=obj.author):
            return True
        return False

    def get_recipes(self, obj):
        recipes = Recipe.objects.filter(author=obj.author)
        return Recipe2SubSerializer(recipes, many=True)

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.author).count()

    def validate(self, data):
        author = self.context.get('author')
        user = self.context['request'].user
        if Subscription.objects.filter(user=user, author=author).exists():
            raise serializers.ValidationError('Вы уже подписаны на этого пользователя.')
        if user == author:
            raise serializers.ValidationError('Нельзя подписаться на себя.')
        return data


class PasswordSerializer(serializers.Serializer):

    new_password = serializers.CharField(
        max_length=consts.PASSWORD_LENGTH, required=True
    )
    current_password = serializers.CharField(
        max_length=consts.PASSWORD_LENGTH, required=True
    )

    def validate(self, data):
        new_password = data['new_password']
        current_password = data['current_password']
        user = self.context['request'].user
        if user.password != current_password:
            raise serializers.ValidationError(
                'Неверный текущий пароль.'
            )
        if new_password == current_password:
            raise serializers.ValidationError(
                'Придумайте новый пароль, который отличается от старого.'
            )
        return data

    def validate_current_password(self, value):
        try:
            User.objects.get(password=value)
        except Exception:
            raise serializers.ValidationError('Неверный текущий пароль.')
        return value


class FavoriteSerializer(serializers.ModelField):
    id = serializers.PrimaryKeyRelatedField(
        source='recipe',
        read_only=True
    )
    name = serializers.ReadOnlyField(source='recipe.name')
    image = serializers.ImageField(
        source='recipe.image',
        read_only=True
    )
    cooking_time = serializers.IntegerField(
        source='recipe.cooking',
        read_only=True
    )

    class Meta:
        model = Favorite
        fields = ('id', 'name', 'image', 'cooking_time')


class ShopCartSerializer(serializers.ModelField):
    id = serializers.PrimaryKeyRelatedField(
        source='recipe',
        read_only=True
    )
    name = serializers.ReadOnlyField(
        source='recipe.name'
    )
    image = serializers.ImageField(
        source='recipe.image',
        read_only=True
    )
    cooking_time = serializers.IntegerField(
        source='recipe.cooking',
        read_only=True
    )

    class Meta:
        model = ShopCart
        fields = ('id', 'name', 'image', 'cooking_time')


class TagSerializer(serializers.ModelSerializer):
    color = Hex2NameColor()

    class Meta:
        model = Tag
        fields = (
            'name', 'color', 'slug'
        )


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = (
            'id', 'name', 'measurement_unit'
        )


class RecipeReadSerializer(serializers.ModelSerializer):
    author = UserSerializer()
    tags = TagSerializer(
        many=True,
        read_only=True
    )
    ingredients = IngredientSerializer(
        many=True,
        read_only=True
    )
    is_favorite = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        )

    def get_is_favorited(self, obj):
        if Favorite.objects.filter(recipe=obj):
            return True
        return False

    def get_is_in_shopping_cart(self, obj):
        if ShopCart.objects.filter(recipe=obj):
            return True
        return False


class RecipeWriteSerializer(serializers.ModelSerializer):
    ingredients = Ingredients2RecipeSerializer(many=True)
    tags = TagSerializer(
        many=True
    )
    image = Base64ImageField()
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())

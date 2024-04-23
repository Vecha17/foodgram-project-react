from django.shortcuts import get_object_or_404
from rest_framework import serializers
import webcolors

from recipes.models import User, Recipe, Tag, Ingredient, Subscription
from recipes import consts
from .mixins import ValidateUsernameMixin


class Hex2NameColor(serializers.Field):

    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        try:
            data = webcolors.hex_to_name(data)
        except ValueError:
            raise serializers.ValidationError('Для этого цвета нет имени')
        return data


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
            'name', 'measurement_unit' #'amount' но это в другой моделе, хз чё делать
        )


class RecipeSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = IngredientSerializer(many=True, read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        )


class Recipe2SubSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionSerializer(serializers.ModelSerializer):
    email = serializers.ReadOnlyField(source='author.email')
    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscriber = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'resipes_count'
        )

    def get_is_subscribed(self, obj):
        if Subscription.objects.filter(user=obj.user, author=obj.author):
            return True
        return False

    def get_resipes(self, obj):
        recipes = Recipe.objects.filter(author=obj.author)
        return Recipe2SubSerializer(recipes, many=True)

    def get_resipes_count(self, obj):
        return Recipe.objects.filter(author=obj.author).count()

    def validate(self, data):
        author = self.context.get('author')
        user = self.context['request'].user
        if Subscription.objects.filter(user=user, author=author):
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

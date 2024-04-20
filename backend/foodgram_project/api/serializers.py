from django.shortcuts import get_object_or_404
from rest_framework import serializers
import webcolors

from recipes.models import User, Recipe, Tag, Ingredient, Subscription
from recipes import consts


class Hex2NameColor(serializers.Field):

    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        try:
            data = webcolors.hex_to_name(data)
        except ValueError:
            raise serializers.ValidationError('Для этого цвета нет имени')
        return data


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username',
            'first_name', 'last_name', 'is_subscribed'
        )


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


class SubscriptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subscription
        fields = ('user', 'subscriber')

    def validate_subscriber(self, value):
        if self.context['request'].user == value:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя!')
        return value


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

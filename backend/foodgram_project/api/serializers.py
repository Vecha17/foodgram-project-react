import base64

from django.core.files.base import ContentFile
from rest_framework import serializers
import webcolors

from recipes import consts
from recipes.models import (
    Amount, Favorite, Ingredient, Recipe, ShopCart,
    Subscription, Tag, User
)

from .mixins import ValidateUsernameMixin


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class HexToNameColor(serializers.Field):

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
            'first_name', 'last_name', 'is_subscribed',
            'password'
        )
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        return user.subscriber.filter(author=obj).exists()
        # Subscription.objects.filter(user=user, author=obj).exists()


class RecipeToSubSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


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
        user = obj.user
        author = obj.author
        return user.subscriber.filter(author=author).exists()
        # if Subscription.objects.filter(user=obj.user, author=obj.author):

    def get_recipes(self, obj):
        author = obj.author
        recipes = author.recipes.all()
        # recipes = Recipe.objects.filter(author=obj.author)
        return RecipeToSubSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        author = obj.author
        return author.recipes.all().count()
        # return Recipe.objects.filter(author=obj.author).count()

    def validate(self, data):
        author = self.context.get('author')
        user = self.context['request'].user
        if user.subscriber.filter(author=author).exists():
            raise serializers.ValidationError(
                'Вы уже подписаны на этого пользователя.'
            )
        if user == author:
            raise serializers.ValidationError(
                'Нельзя подписаться на себя.'
            )
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


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')
        read_only_fields = ('__all__',)


class FavoriteSerializer(serializers.ModelSerializer):
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
        source='recipe.cooking_time',
        read_only=True
    )

    class Meta:
        model = Favorite
        fields = ('id', 'name', 'image', 'cooking_time')


class ShopCartSerializer(serializers.ModelSerializer):
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
        source='recipe.cooking_time',
        read_only=True
    )

    class Meta:
        model = ShopCart
        fields = ('id', 'name', 'image', 'cooking_time')


class TagSerializer(serializers.ModelSerializer):
    color = HexToNameColor()

    class Meta:
        model = Tag
        fields = (
            'id', 'name', 'color', 'slug'
        )


class IngredientAmountSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(
        source='ingredient.id'
    )
    name = serializers.ReadOnlyField(
        source='ingredient.name'
    )
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = Amount
        fields = (
            'id', 'name', 'measurement_unit', 'amount'
        )


class RecipeReadSerializer(serializers.ModelSerializer):
    author = UserSerializer()
    tags = TagSerializer(
        many=True,
        read_only=True
    )
    ingredients = IngredientAmountSerializer(
        many=True,
        source='recipe_ingredients',
    )
    is_favorite = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorite',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        )

    def get_is_favorite(self, obj):
        recipe = obj
        return recipe.favorite.exists()
        # if Favorite.objects.filter(recipe=obj):

    def get_is_in_shopping_cart(self, obj):
        recipe = obj
        return recipe.shop_cart.exists()
        # if ShopCart.objects.filter(recipe=obj):


class IngredientsToRecipeSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )
    amount = serializers.IntegerField(
        min_value=consts.MIN_VALUE_VALID,
        max_value=consts.MAX_VALUE_VALID
    )

    class Meta:
        model = Amount
        fields = ('id', 'amount')


class RecipeWriteSerializer(serializers.ModelSerializer):
    ingredients = IngredientsToRecipeSerializer(
        many=True,
        write_only=True
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    image = Base64ImageField()
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())
    cooking_time = serializers.IntegerField(
        min_value=consts.MIN_VALUE_VALID,
        max_value=consts.MAX_VALUE_VALID
    )

    class Meta:
        model = Recipe
        fields = (
            'ingredients', 'tags', 'image',
            'name', 'text', 'cooking_time', 'author'
        )

    def to_representation(self, instance):
        serializer = RecipeReadSerializer(instance,)
        return serializer.data

    def create_ingredients(self, ingredients, recipe):
        for ingredient in ingredients:
            id = ingredient['id']
            ingredient = Ingredient.objects.get(pk=id)
            amount = ingredient['amount']
            Amount.objects.create(
                ingredient=ingredient, recipe=recipe, amount=amount
            )

    def create_tags(self, tags, recipe):
        recipe.tags.set(tags)

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data,)
        self.create_ingredients(ingredients, recipe)
        self.create_tags(tags, recipe)
        return recipe

    def update(self, instance, validated_data):
        Amount.objects.filter(recipe=instance).delete()
        Tag.objects.filter(recipe=instance).delete()
        self.create_ingredients(validated_data.pop('ingredients'), instance)
        self.create_tags(validated_data.pop('tags'), instance)
        return super().update(instance, validated_data)
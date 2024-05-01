from django.shortcuts import get_object_or_404
from rest_framework import filters, generics, status, views, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import (
    IsAuthenticatedOrReadOnly, SAFE_METHODS,
    AllowAny, IsAuthenticated
)
from django_filters.rest_framework import DjangoFilterBackend

from recipes.models import User, Recipe, Tag, Ingredient, Subscription
from .serializers import UserSerializer, RecipeReadSerializer, TagSerializer, IngredientSerializer, PasswordSerializer, SubscriptionSerializer, RecipeWriteSerializer, FavoriteSerializer
from .paginations import Pagination


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = Pagination

    @action(
            detail=False,
            methods=['get',],
            url_path='me',
            permission_classes=(IsAuthenticated,)
    )
    def me(self):
        user = get_object_or_404(User, username=self.request.user.username)
        serializer = self.get_serializer(user, many=False)
        return Response(serializer.data)

    @action(
            detail=False,
            methods=['post',],
            url_path='set_password',
            permission_classes=(IsAuthenticated,),
    )
    def set_password(self, request):
        serializer = PasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.get_object()
        user.set_password(serializer.data.get('new_password'))
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
            detail=False,
            methods=['get',],
            url_path='subscriptions',
            permission_classes=(IsAuthenticated,),
            pagination_class=Pagination
    )
    def subscriptions(self, request):
        subscriptions = Subscription.objects.filter(user_id=request.user.id)
        serializer = SubscriptionSerializer(
            subscriptions,
            many=True,
        )
        return Response(serializer.data)

    @action(
            detail=True,
            methods=['post', 'delete'],
            url_path='subscribe',
            permission_classes=(IsAuthenticated,),
    )
    def subscribe(self, request, pk=None):
        user = request.user
        author = get_object_or_404(User, id=pk)
        if request.method == 'POST':
            serializer = SubscriptionSerializer(
                data=request.data,
                context={'request': request, 'author': author}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(user=user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        Subscription.objects.filter(author=author).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_serializer_class(self):
        if self.action == 'set_password':
            return PasswordSerializer
        elif self.action == ('subscriptions' or 'subscribe'):
            return SubscriptionSerializer
        return UserSerializer


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    search_fields = ('name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeReadSerializer
    pagination_class = Pagination

    @action(
        detail=True,
        methods=['post', 'delete'],
        url_path='favorite',
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk=None):
        recipe = get_object_or_404(Recipe, id=pk)
        user = request.user
        if request.method == 'POST':
            serializer = FavoriteSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(author=user, recipe=recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        Ingredient.objects.filter(user=user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


from django.shortcuts import get_object_or_404
from rest_framework import filters, generics, status, views, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import (PageNumberPagination,)
from rest_framework.permissions import (
    IsAuthenticatedOrReadOnly, SAFE_METHODS,
    AllowAny, IsAuthenticated
)

from recipes.models import User, Recipe, Tag, Ingredient
from .serializers import UserSerializer, RecipeSerializer, TagSerializer, IngredientSerializer, PasswordSerializer, SubscriptionSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny, )
    http_method_names = ('get', 'post')
    #filter_backends = (filters.SearchFilter,)
    #lookup_field = 'username'
    pagination_class = (PageNumberPagination)

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
            url_path='subscribtions',
            permission_classes=(IsAuthenticated,),
    )
    def subscribtions(self, request):
        user = get_object_or_404(User, username=request.user.username)
        sub = user.subscribers
        serializer = SubscriptionSerializer(sub, many=True)
        return Response(serializer.data)
    #ДОДЕЛАТЬ

    @action(
            detail=True,
            methods=['post', 'delete'],
            url_path='subscribe',
            permission_classes=(IsAuthenticated,),
    )
    def subscribe(self, request, pk=None):
    #ДОДЕЛАТЬ

    def get_serializer_class(self):
        if self.action == 'set_password':
            return PasswordSerializer
        elif self.action == 'subscriptions':
            return SubscriptionSerializer
        return UserSerializer


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    #доделать


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)

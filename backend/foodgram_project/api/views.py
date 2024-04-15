from django.shortcuts import get_object_or_404
from rest_framework import filters, generics, status, views, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import (PageNumberPagination)
from rest_framework.permissions import (
    IsAuthenticatedOrReadOnly, SAFE_METHODS,
    AllowAny, IsAuthenticated
)

from recipes.models import User
from .serializers import UserSerializer


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

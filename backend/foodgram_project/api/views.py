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
from serializers import UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    #permission_classes = (AdminOnly, )
    http_method_names = ('get', 'post', 'patch', 'delete')
    #filter_backends = (filters.SearchFilter,)
    #lookup_field = 'username'
    pagination_class = (PageNumberPagination)

    @action(
            detail=False,
            methods=['get', 'patch'],
            url_path='me',
            permission_classes=(IsAuthenticated,)
    )
    def me(self, request):
        if request.method == 'GET':
            user = get_object_or_404(User, username=self.request.user.username)
            serializer = self.get_serializer(user, many=False)
            return Response(serializer.data)
        user = self.request.user
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(status=status.HTTP_400_BAD_REQUEST)

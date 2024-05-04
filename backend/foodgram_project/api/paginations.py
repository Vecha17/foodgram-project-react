from rest_framework.pagination import PageNumberPagination

from recipes import consts


class Pagination(PageNumberPagination):
    page_size_query_param = "limit"
    page_size = consts.OBJECT_ON_PAGE

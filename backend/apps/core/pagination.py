"""API uchun sahifalash sinflari."""

from rest_framework.pagination import PageNumberPagination


class StandardPagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = "page_size"
    max_page_size = 60


class LargePagination(StandardPagination):
    page_size = 30
    max_page_size = 100

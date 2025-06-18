from rest_framework.pagination import PageNumberPagination

from .constants import PAGINATION_PAGE_COUNT


class CustomPageNumberPagination(PageNumberPagination):
    """Кастомная пагинация с ограничением на количество
    элементов на странице."""
    page_size = PAGINATION_PAGE_COUNT
    page_size_query_param = "limit"

from django_filters import rest_framework as filters
import django_filters

from recipes.models import Recipe, Tag
from rest_framework import filters as drf_filters


class RecipeFilter(filters.FilterSet):
    """Фильтр рецептов с возможностью фильтрации по
    наличию в списке покупок, избранном, по тегам и автору.
    """

    is_in_shopping_cart = django_filters.BooleanFilter(
        method="filter_is_in_shopping_cart"
    )
    is_favorited = django_filters.BooleanFilter(method="filter_is_favorited")
    tags = filters.ModelMultipleChoiceFilter(
        field_name="tags__slug",
        to_field_name="slug",
        queryset=Tag.objects.all(),
    )

    class Meta:
        model = Recipe
        fields = {
            'tags': ['exact'],
            'author': ['exact'],
        }

    def filter_is_in_shopping_cart(self, queryset, name, value):
        """Фильтр по факту наличия в корзине"""
        author = self.request.user
        if value and author.is_authenticated:
            return queryset.filter(in_carts__user=author)
        return queryset

    def filter_is_favorited(self, queryset, name, value):
        """Фильтр по факту наличия в избранном"""
        author = self.request.user
        if value and author.is_authenticated:
            return queryset.filter(in_favorites__user=author)
        return queryset


class IngredientSearchFilter(drf_filters.SearchFilter):
    """Фильтр ингредиентов по названию"""
    search_param = 'name'

import django_filters
from django_filters import rest_framework as filters
from recipes.models import Recipe, Tag
from rest_framework import filters as drf_filters


class RecipeFilter(filters.FilterSet):
    """Фильтр для рецептов с возможностью фильтрации по:
    - Наличию в списке покупок
    - Наличию в избранном
    - Тегам (множественный выбор)
    - Автору
    """

    is_in_shopping_cart = django_filters.CharFilter(
        method="filter_is_in_shopping_cart"
    )
    is_favorited = django_filters.CharFilter(method="filter_is_favorited")
    tags = filters.ModelMultipleChoiceFilter(
        field_name="tags__slug",
        to_field_name="slug",
        queryset=Tag.objects.all(),
    )
    author = filters.NumberFilter(field_name='author__id')

    class Meta:
        model = Recipe
        fields = ("tags", "author", "is_in_shopping_cart", "is_favorited")

    def filter_is_in_shopping_cart(self, queryset, name, value):
        author = self.request.author
        if value and author.is_authenticated:
            return queryset.filter(cart_recipes__author=author)
        return queryset

    def filter_is_favorited(self, queryset, name, value):
        author = self.request.author
        if value and author.is_authenticated:
            return queryset.filter(favorite_recipes__author=author)
        return queryset


class IngredientSearchFilter(drf_filters.SearchFilter):
    """Фильтр для поиска ингредиентов по названию."""
    search_param = 'name'

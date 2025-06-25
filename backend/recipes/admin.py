from django.contrib import admin
from django.core.exceptions import ValidationError

from .models import (Ingredient,
                     Recipe,
                     Tag,
                     Favorite,
                     Cart,
                     AmountIngredientInRecipe)


class AmountIngredientInRecipeInline(admin.TabularInline):
    model = AmountIngredientInRecipe
    extra = 1
    min_num = 1
    autocomplete_fields = ['ingredient']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    fields = ('name', 'measurement_unit')
    search_fields = ('name',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = [AmountIngredientInRecipeInline]
    list_display = ('name', 'author', 'favorites_count')
    search_fields = ('name', 'author__username')
    list_filter = ('tags',)

    def favorites_count(self, obj):
        return obj.in_favorites.count()

    def save_model(self, request, obj, form, change):
        if not obj.image:
            raise ValidationError("Нельзя загрузить рецепт без изображения.")
        super().save_model(request, obj, form, change)


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'user')


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'user')

from random import choices

import unidecode
from api.constants import (MAX_LENGTH_INGREDIENT_NAME,
                           MAX_LENGTH_MEASUREMENT_UNIT, MAX_LENGTH_RECIPE_NAME,
                           MAX_LENGTH_SHORT_LINK, MAX_LENGTH_TAG_NAME,
                           MAX_LENGTH_TAG_SLUG, MIN_COOKING_TIME,
                           MIN_INGREDIENT_AMOUNT, ALLOWED_CHARS)
from autoslug import AutoSlugField
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from users.models import User


def transliterate_slugify(value):
    """Транслитерирует кириллицу в латиницу перед slugify."""
    return unidecode.unidecode(value)


class Ingredient(models.Model):
    "Модель для ингридиентов."
    name = models.CharField(
        max_length=MAX_LENGTH_INGREDIENT_NAME
    )
    measurement_unit = models.CharField(
        max_length=MAX_LENGTH_MEASUREMENT_UNIT
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['name',
                        'measurement_unit'],
                name='unique_ingredient_and_name_measurement'
            )
        ]

    def __str__(self):
        return f"{self.name} ({self.measurement_unit})"


class Tag(models.Model):
    "Модель для тегов."
    name = models.CharField(
        max_length=MAX_LENGTH_TAG_NAME,
        unique=True,
    )
    slug = AutoSlugField(
        populate_from='name',
        unique=True,
        slugify=transliterate_slugify,
        max_length=MAX_LENGTH_TAG_SLUG,
        editable=False,
    )

    class Meta:
        verbose_name = 'тег'
        verbose_name_plural = 'теги'
        ordering = ['name']

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField(max_length=MAX_LENGTH_RECIPE_NAME)
    text = models.TextField()
    cooking_time = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(MIN_COOKING_TIME)]
    )
    image = models.ImageField(
        upload_to='recipes/',
        blank=False,
        default="",
        null=False
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
    )
    tags = models.ManyToManyField(Tag, related_name="recipes")
    created_at = models.DateTimeField(auto_now_add=True)

    short_link = models.CharField(
        max_length=MAX_LENGTH_SHORT_LINK,
        blank=True,
        null=True,
        unique=True,
    )

    def generate_short_link(self):
        "Генерирует уникальный короткий ключ"
        slug = ''.join(choices(ALLOWED_CHARS, k=MAX_LENGTH_SHORT_LINK))
        if not Recipe.objects.filter(short_link=slug).exists():
            return slug
        raise ValidationError("""Не удалось сгенерировать
                                  уникальный короткий URL""")

    class Meta:
        """ """
        ordering = ['-created_at']

    def __str__(self):
        """ """
        return f"Рецепт: {self.name} (ID: {self.id})"  #


class AmountIngredientInRecipe(models.Model):
    """ """

    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipes_with_ingredient',
    )
    amount = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(MIN_INGREDIENT_AMOUNT)
        ]
    )

    class Meta:
        """ """

        ordering = ('recipe',)
        constraints = [
            models.UniqueConstraint(
                name='unique_pair_of_recipe_and_ingredient',
                fields=['recipe', 'ingredient'],

            )
        ]

    def __str__(self):
        return f'{self.ingredient} — {self.amount} (для {self.recipe})'  #


class BaseChoiceModel(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        'Recipe',
        on_delete=models.CASCADE,
    )

    class Meta:
        abstract = True
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_user_recipe_%(class)s'
            )
        ]
        default_related_name = 'in_%(class)ss'
        ordering = ['recipe__name']


class Favorite(BaseChoiceModel):
    class Meta(BaseChoiceModel.Meta):
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'


class Cart(BaseChoiceModel):
    class Meta(BaseChoiceModel.Meta):
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'

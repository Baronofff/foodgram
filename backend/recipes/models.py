import unidecode

from autoslug import AutoSlugField
from django.db import models

from api.constants import (MAX_LENGTH_INGREDIENT_NAME,
                           MAX_LENGTH_MEASUREMENT_UNIT, MAX_LENGTH_TAG_NAME,
                           MAX_LENGTH_TAG_SLUG)


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
                fields=['name', 'measurement_unit'],
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
        pass

    def __str__(self):
        return self.name

from django.contrib.auth import get_user_model
from drf_extra_fields.fields import Base64ImageField
from recipes.models import (AmountIngredientInRecipe, Cart, Favorite,
                            Ingredient, Recipe, Tag)
from rest_framework import serializers
from users.models import Subscription

User = get_user_model()


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Упрощенное представление рецептов"""
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")


class AvatarSerializer(serializers.ModelSerializer):
    """Обработка аватара пользователя"""
    avatar = Base64ImageField(required=True)

    class Meta:
        model = User
        fields = ('avatar',)


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор профиля пользователя"""
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username',
            'first_name', 'last_name', 'avatar',
            'is_subscribed',
        )

    def get_is_subscribed(self, instance):
        """Проверка подписки на пользователя"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Subscription.objects.filter(
                author=instance,  # на кого подписываются
                subscribers=request.user  # кто подписывается
            ).exists()
        return False


class FollowCreateSerializer(serializers.Serializer):
    """Обработчик создания подписок"""

    def validate(self, attrs):
        """Проверка возможности подписки"""
        request = self.context['request']
        target_user = self.context['author']
        user = request.user

        if user == target_user:
            raise serializers.ValidationError(
                "Подписка на себя невозможна"
            )
        if Subscription.objects.filter(user=request.user,
                                       author=target_user).exists():
            raise serializers.ValidationError(
                "Подписка уже существует"
            )
        return attrs

    def create(self, validated_data):
        """Создание новой подписки"""
        request = self.context['request']
        target_user = self.context['author']

        return Subscription.objects.create(user=request.user,
                                           author=target_user)


class FollowTerminationValidator(serializers.Serializer):
    """Валидатор отмены подписки"""

    def validate(self, attrs):
        """Проверка существования подписки"""
        request = self.context['request']
        target_user = self.context['author']

        if not Subscription.objects.filter(user=request.user,
                                           author=target_user).exists():
            raise serializers.ValidationError(
                "Подписка не найдена"
            )
        return attrs


class FollowSerializer(serializers.ModelSerializer):
    """Представление подписок"""
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count', 'avatar'
        )

    def get_is_subscribed(self, instance):
        """Проверка активной подписки"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Subscription.objects.filter(
                user=request.user,
                author=instance
            ).exists()
        return False

    def get_recipes(self, instance):
        """Получение рецептов с ограничением"""
        request = self.context.get("request")
        limit = request.GET.get("recipes_limit")
        recipe_set = instance.recipes.all()

        if limit and limit.isdigit():
            recipe_set = recipe_set[:int(limit)]

        return RecipeCustomSerializer(
            recipe_set,
            many=True,
            context=self.context
        ).data

    def get_recipes_count(self, instance):
        """Подсчет рецептов пользователя"""
        return instance.recipes.count()

    def get_avatar(self, instance):
        """Получение URL аватара"""
        avatar_serializer = AvatarSerializer(
            instance,
            context=self.context
        )
        return avatar_serializer.data.get('avatar')


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тегов"""

    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug']


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов"""

    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'measurement_unit']


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Связь рецептов и ингредиентов"""
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = AmountIngredientInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeDetailSerializer(serializers.ModelSerializer):
    """Детальное представление рецепта"""
    author = serializers.SerializerMethodField()
    tags = TagSerializer(many=True, read_only=True)
    ingredients = RecipeIngredientSerializer(
        many=True,
        source="recipes_with_ingredient",
        read_only=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = [
            "id", "tags", "author", "ingredients",
            "is_favorited", "is_in_shopping_cart", "name",
            "image", "text", "cooking_time"
        ]

    def get_image(self, obj):
        """Генерация URL изображения"""
        if obj.image:
            request = self.context.get('request')
            return request.build_absolute_uri(
                obj.image.url) if request else obj.image.url
        return ""

    def get_is_favorited(self, obj):
        """Проверка наличия в избранном"""
        user = self.context["request"].user
        return user.is_authenticated and Favorite.objects.filter(
            user=user, recipe=obj
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        """Проверка наличия в корзине"""
        user = self.context["request"].user
        return user.is_authenticated and Cart.objects.filter(
            user=user, recipe=obj
        ).exists()

    def get_author(self, obj):
        """Используем author"""
        return UserSerializer(obj.author, context=self.context).data


class RecipeEditorSerializer(serializers.ModelSerializer):
    """Редактор рецептов"""
    image = Base64ImageField(required=True)
    ingredients = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        required=True
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        required=True
    )

    class Meta:
        model = Recipe
        fields = (
            "id", "ingredients", "tags", "image",
            "name", "text", "cooking_time"
        )
        read_only_fields = ("id", "author")

    def validate_ingredients(self, items):
        """Валидация ингредиентов"""
        if not items:
            raise serializers.ValidationError("Требуются ингредиенты")

        ids = [item['id'] for item in items]
        if len(ids) != len(set(ids)):
            raise serializers.ValidationError("Дубликаты ингредиентов")

        validated = []
        for item in items:
            if 'id' not in item or 'amount' not in item:
                raise serializers.ValidationError(
                    "Неполные данные ингредиента")

            try:
                ingredient = Ingredient.objects.get(id=item['id'])
            except Ingredient.DoesNotExist:
                raise serializers.ValidationError(
                    f"Ингредиент {item['id']} не найден")

            if int(item['amount']) <= 0:
                raise serializers.ValidationError("Некорректное количество")

            validated.append({
                'id': ingredient.id,
                'amount': item['amount']
            })
        return validated

    def validate(self, data):
        """Общая валидация рецепта"""
        request = self.context['request']

        if request.method in ['PUT', 'PATCH']:
            if 'ingredients' not in data:
                raise serializers.ValidationError(
                    {'ingredients': 'Обязательное поле'})

        if not data.get('tags'):
            raise serializers.ValidationError({'tags': 'Требуются теги'})

        if self.context['request'].method == 'POST' and not data.get('image'):
            raise serializers.ValidationError(
                {'image': 'Требуется изображение'})

        if len(data['tags']) != len(set(data['tags'])):
            raise serializers.ValidationError({'tags': 'Дубликаты тегов'})

        if data.get('cooking_time', 0) < 1:
            raise serializers.ValidationError(
                {'cooking_time': 'Минимум 1 минута'})

        if request.method == 'POST' and not data.get('image'):
            raise serializers.ValidationError(
                {'image': 'Требуется изображение'})

        return data

    def process_ingredients(self, recipe, ingredients):
        """Обработка ингредиентов рецепта"""
        AmountIngredientInRecipe.objects.bulk_create([
            AmountIngredientInRecipe(
                recipe=recipe,
                ingredient_id=item['id'],
                amount=item['amount']
            ) for item in ingredients
        ])

    def create(self, validated_data):
        """Создание рецепта"""
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(
            author=self.context['request'].user,
            **validated_data
        )
        recipe.tags.set(tags)
        self.process_ingredients(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        "Обновление рецепта"
        ingredients = validated_data.pop('ingredients', None)
        tags = validated_data.pop('tags', None)

        if tags is not None:
            instance.tags.set(tags)

        if ingredients is not None:
            instance.recipes_with_ingredient.all().delete()
            self.process_ingredients(instance, ingredients)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        return instance

    def to_representation(self, instance):
        """Сериализация результата"""
        return RecipeDetailSerializer(
            instance,
            context=self.context
        ).data


class RecipeMinimalSerializer(serializers.ModelSerializer):
    """Минималистичное представление рецепта"""
    image = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')

    def get_image(self, obj):
        """Обработка изображения"""
        request = self.context.get('request')
        if not obj.image:
            return ""
        return request.build_absolute_uri(
            obj.image.url) if request else obj.image.url


class RecipeCustomSerializer(serializers.ModelSerializer):
    """Сериализатор для кастомного отображения рецептов."""

    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")


class BaseUserRecipeSerializer(serializers.ModelSerializer):
    """Базовый сериализатор отношений"""
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        fields = ('user', 'recipe')
        read_only_fields = ('user',)

    def validate(self, data):
        """Проверка уникальности"""
        user = data['user']
        recipe = data['recipe']
        if self.Meta.model.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError("Уже существует")
        return data

    def to_representation(self, instance):
        return RecipeMinimalSerializer(
            instance.recipe,
            context=self.context
        ).data


class FavoriteItemsSerializer(BaseUserRecipeSerializer):
    """Сериализатор избранного"""
    class Meta(BaseUserRecipeSerializer.Meta):
        model = Favorite


class CartItemsSerializer(BaseUserRecipeSerializer):
    """Сериализатор корзины"""
    class Meta(BaseUserRecipeSerializer.Meta):
        model = Cart

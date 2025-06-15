from django.db.models import Sum
from django.http import HttpResponse  # , HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet
from recipes.models import (AmountIngredientInRecipe, Cart, Favorite,
                            Ingredient, Recipe, Tag)
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated  # AllowAny,
from rest_framework.response import Response
from users.models import Subscription, User

from .filters import IngredientSearchFilter, RecipeFilter
from .pagination import PageLimitPagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (AvatarSerializer, CartItemsSerializer,
                          FavoriteItemsSerializer, FollowCreateSerializer,
                          FollowSerializer, FollowTerminationValidator,
                          IngredientSerializer, RecipeDetailSerializer,
                          RecipeEditorSerializer, TagSerializer,
                          UserSerializer)


class UserViewSet(DjoserUserViewSet):
    """ViewSet для работы с пользователями."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = PageLimitPagination

    def get_permissions(self):
        """Определение разрешений для действия 'me'."""
        if self.action == "me":
            return [IsAuthenticated()]
        return super().get_permissions()

    @action(
        detail=False,
        methods=['put'],
        permission_classes=[IsAuthenticated],
        url_path='me/avatar'
    )
    def avatar(self, request):
        """Обновление аватара пользователя."""
        user = request.user
        serializer = AvatarSerializer(
            user,
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @avatar.mapping.delete
    def delete_avatar(self, request):
        """Удаление аватара пользователя."""
        user = request.user
        if user.avatar:
            user.avatar.delete()
            user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthenticated],
        url_path='subscribe'
    )
    def subscribe(self, request, id=None):
        """Подписка на пользователя."""
        author = get_object_or_404(User, id=id)
        serializer = FollowCreateSerializer(
            data=request.data,
            context={'request': request, 'author': author}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        response_serializer = FollowSerializer(
            author, context={'request': request}
        )
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def unsubscribe(self, request, id=None):
        """Отписка от пользователя."""
        author = get_object_or_404(User, id=id)
        serializer = FollowTerminationValidator(
            data={}, context={'request': request, 'author': author}
        )
        serializer.is_valid(raise_exception=True)
        Subscription.objects.filter(user=request.user, author=author).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated],
        pagination_class=PageLimitPagination
    )
    def subscriptions(self, request):
        """Получение списка подписок пользователя."""
        author = request.author
        queryset = User.objects.filter(subscriptions__author=author)
        pages = self.paginate_queryset(queryset)
        serializer = FollowSerializer(
            pages, many=True, context={"request": request}
        )
        return self.get_paginated_response(serializer.data)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для работы с тегами."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для работы с ингредиентами."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = [IngredientSearchFilter]
    search_fields = ['^name']


class RecipeViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с рецептами."""

    queryset = Recipe.objects.all()
    serializer_class = RecipeDetailSerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        IsAuthorOrReadOnly,
    ]
    pagination_class = PageLimitPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от действия."""
        if self.action in ("create", "update", "partial_update"):
            return RecipeEditorSerializer
        return RecipeDetailSerializer

    def create(self, request, *args, **kwargs):
        editor_serializer = RecipeEditorSerializer(
            data=request.data,
            context={'request': request}
        )
        editor_serializer.is_valid(raise_exception=True)

        recipe = editor_serializer.save()

        detail_serializer = RecipeDetailSerializer(
            recipe,
            context={'request': request}
        )

        headers = self.get_success_headers(detail_serializer.data)
        return Response(
            detail_serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthenticated],
        url_path='(?P<type>favorite|shopping_cart)'
    )
    def add_to_list(self, request, pk=None, type=None):
        """Добавление рецепта в избранное или список покупок."""
        recipe = get_object_or_404(Recipe, id=pk)
        if type == 'shopping_cart':
            serializer_class = CartItemsSerializer
        elif type == 'favorite':
            serializer_class = FavoriteItemsSerializer
        else:
            return Response(
                {'errors': 'Неверный тип действия'},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = serializer_class(
            data={'recipe': recipe.id},
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @add_to_list.mapping.delete
    def remove_from_list(self, request, pk=None, type=None):
        """Удаление рецепта из избранного или списка покупок."""
        recipe = get_object_or_404(Recipe, id=pk)
        user = request.user
        if type == 'shopping_cart':
            relation_model = Cart
        elif type == 'favorite':
            relation_model = Favorite
        else:
            return Response(
                {'errors': 'Неверный тип действия'},
                status=status.HTTP_400_BAD_REQUEST
            )
        deleted_count, _ = relation_model.objects.filter(
            user=request.user, recipe=recipe
        ).delete()
        if not deleted_count:
            return Response(
                {'errors': 'Рецепт не найден в списке'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated],
        url_path='download_shopping_cart'
    )
    def download_shopping_cart(self, request):
        """Скачивание списка покупок в виде текстового файла."""
        ingredients = AmountIngredientInRecipe.objects.filter(
            recipe__in=Cart.objects.filter(
                user=request.user
            ).values('recipe')
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(total=Sum('amount'))

        text = 'Список покупок:\n\n'
        for ing in ingredients:
            text += (
                f"{ing['ingredient__name']} "
                f"({ing['ingredient__measurement_unit']}) - "
                f"{ing['total']}\n"
            )
        response = HttpResponse(text, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="shopping_list.txt"'
        return response

    @action(
        detail=True,
        methods=['get'],
        permission_classes=[permissions.AllowAny],
        url_path='get-link'
    )
    def get_link(self, request, pk=None):
        """
        Возвращает короткую ссылку на рецепт.
        Если ссылка не создана — создаёт ее.
        """
        recipe = self.get_object()
        if not recipe.short_link:
            recipe.short_link = recipe.generate_short_link()
            recipe.save()
        short_link = f"{request.get_host()}/{recipe.short_link}/"
        return Response({'short-link': short_link}, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if 'image' in request.data and not request.data['image']:
            return Response(
                {'image': ['Это поле не может быть пустым']},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = self.get_serializer(instance, data=request.data, partial=kwargs.pop('partial', False))
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)

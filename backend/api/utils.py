from recipes.models import UserRecipeRelation

RELATION_TYPE_CHOICES = {
    'favorite': UserRecipeRelation.FAVORITE,
    'shopping_cart': UserRecipeRelation.CART,
}

RELATION_ERROR_MESSAGES = {
    'favorite': {
        'exists': 'Рецепт уже в избранном',
        'not_exists': 'Рецепта нет в избранном',
    },
    'shopping_cart': {
        'exists': 'Рецепт уже в корзине',
        'not_exists': 'Рецепта не было в корзине',
    },
}


def get_errors_and_relations(action_type):
    """
    Возвращает сообщения об ошибках и тип отношения для указанного действия.

    Args:
        action_type: Тип действия ('favorite' или 'shopping_cart')

    Returns:
        tuple: (сообщения_об_ошибках, тип_отношения)

    Raises:
        ValueError: Если передан недопустимый тип действия
    """
    if action_type not in RELATION_TYPE_CHOICES:
        raise ValueError('Недопустимый тип действия')

    relation_type = RELATION_TYPE_CHOICES[action_type]
    error_messages = RELATION_ERROR_MESSAGES[action_type]

    return error_messages, relation_type

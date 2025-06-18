from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from users.models import User


class IsReadOnlyOrAuthor(IsAuthenticated):
    """Проверка прав доступа
    для доступа чтения для всех,
    а изменения только для автора."""

    def has_permission(self, request, view):
        """Проверяет общие права доступа"""

        return request.method in SAFE_METHODS or isinstance(request.user, User)

    def has_object_permission(self, request, view, obj):
        """Проверяет права доступа к определенному объекту"""

        return request.method in SAFE_METHODS or obj.author == request.user

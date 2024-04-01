from rest_framework.permissions import SAFE_METHODS, IsAuthenticated


class IsCreatorOrOwnerOrReadOnly(IsAuthenticated):
    """
    Класс прав доступа чтение - авторизованным пользователям,
    редактирование - только создателю или владельцу объекта."""

    def has_object_permission(self, request, view, obj):
        return bool(
            request.method in SAFE_METHODS
            and (request.user == (obj.owner or obj.creator))
        )

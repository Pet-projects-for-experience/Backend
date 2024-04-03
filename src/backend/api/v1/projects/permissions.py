from rest_framework.permissions import SAFE_METHODS, IsAuthenticated


class IsCreatorOrOwner(IsAuthenticated):
    """
    Класс прав доступа на чтение и редактирование только создателю или
    владельцу объекта.
    """

    def has_object_permission(self, request, view, obj):
        return bool(request.user == (obj.owner or obj.creator))


class IsCreatorOrOwnerOrReadOnly(IsAuthenticated):
    """
    Класс прав доступа чтение - любому авторизованному пользователю, а
    редактирование только создателю или владельцу объекта.
    """

    def has_object_permission(self, request, view, obj):
        return bool(
            request.method in SAFE_METHODS
            or request.user == (obj.owner or obj.creator)
        )

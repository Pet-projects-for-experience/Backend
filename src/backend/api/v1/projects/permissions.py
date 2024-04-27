from rest_framework.permissions import SAFE_METHODS, AllowAny, IsAuthenticated


class IsCreatorOrOwner(IsAuthenticated):
    """
    Класс прав доступа на чтение и редактирование только создателю или
    владельцу объекта.
    """

    def has_object_permission(self, request, view, obj):
        return bool(request.user in (obj.owner, obj.creator))


class IsCreatorOrOwnerOrReadOnly(AllowAny):
    """
    Класс прав доступа чтение - любому пользователю, а редактирование только
    создателю или владельцу объекта.
    """

    def has_object_permission(self, request, view, obj):
        return bool(
            request.method in SAFE_METHODS
            or request.user in (obj.owner, obj.creator)
        )


class IsProjectCreatorOrOwner(IsAuthenticated):
    """
    Класс прав доступа на чтение и редактирование только создателю или
    владельцу проекта.
    """

    def has_object_permission(self, request, view, obj):
        return bool(request.user in (obj.project.owner, obj.project.creator))

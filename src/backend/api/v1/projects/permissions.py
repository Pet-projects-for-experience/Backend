from rest_framework.permissions import SAFE_METHODS, AllowAny, IsAuthenticated

from apps.projects.models import RequestStatuses


class IsCreatorOrOwner(IsAuthenticated):
    """
    Класс прав доступа на чтение и редактирование только создателю или
    владельцу объекта.
    """

    def has_object_permission(self, request, view, obj) -> bool:
        return bool(request.user in (obj.owner, obj.creator))


class IsCreatorOrOwnerOrReadOnly(AllowAny):
    """
    Класс прав доступа чтение - любому пользователю, а редактирование только
    создателю или владельцу объекта.
    """

    def has_object_permission(self, request, view, obj) -> bool:
        return bool(
            request.method in SAFE_METHODS
            or request.user in (obj.owner, obj.creator)
        )


class IsParticipationRequestCreatorOrProjectCreatorOrOwnerReadOnly(
    IsAuthenticated
):
    """
    Класс прав доступа на чтение и редактирование только создателю запроса или
    создателю или владельцу проекта только на чтение.
    """

    def has_object_permission(self, request, view, obj) -> bool:
        return bool(
            request.user == obj.user
            and (
                obj.status == RequestStatuses.IN_PROGRESS
                or request.method == "DELETE"
            )
            or (
                request.method in SAFE_METHODS
                and request.user in (obj.project.owner, obj.project.creator)
            )
        )


class IsProjectCreatorOrOwner(IsAuthenticated):
    """
    Класс прав доступа на чтение и редактирование только создателю или
    владельцу проекта.
    """

    def has_object_permission(self, request, view, obj) -> bool:
        return bool(request.user in (obj.project.owner, obj.project.creator))


class IsProjectCreatorOrOwnerForParticipationRequest(IsProjectCreatorOrOwner):
    """
    Класс прав доступа на чтение и редактирование только создателю или
    владельцу проекта.
    """

    def has_object_permission(self, request, view, obj) -> bool:
        return bool(
            obj.status
            not in (
                RequestStatuses.ACCEPTED,
                RequestStatuses.REJECTED,
            )
            and request.user in (obj.project.owner, obj.project.creator)
        )


class IsInvitationAuthorOrUser(IsAuthenticated):
    def has_object_permission(self, request, view, obj) -> bool:
        return request.user in (obj.user, obj.author)

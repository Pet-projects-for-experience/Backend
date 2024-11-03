from django.contrib.auth.models import AnonymousUser
from django.db.models import Prefetch, Q, QuerySet
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer
from rest_framework.viewsets import (
    GenericViewSet,
    ModelViewSet,
    ReadOnlyModelViewSet,
)

from api.v1.projects.filters import MyRequestsFilter, ProjectFilter
from api.v1.projects.paginations import (
    ProjectPagination,
    ProjectPreviewMainPagination,
)
from api.v1.projects.permissions import (
    IsCreatorOrOwner,
    IsCreatorOrOwnerOrReadOnly,
    IsInvitationAuthorOrUser,
    IsParticipationRequestCreatorOrProjectCreatorOrOwnerReadOnly,
    IsProjectCreatorOrOwner,
    IsProjectCreatorOrOwnerForParticipationRequest,
)
from api.v1.projects.serializers import (
    DirectionSerializer,
    MyRequestsSerializer,
    PartialWriteInvitationToProjectSerializer,
    ProjectPreviewMainSerializer,
    ReadDraftSerializer,
    ReadListParticipationRequestSerializer,
    ReadProjectSerializer,
    WriteDraftSerializer,
    WriteInvitationToProjectSerializer,
    WriteParticipationRequestAnswerSerializer,
    WriteParticipationRequestSerializer,
    WriteProjectSerializer,
    WriteProjectSpecialistSerializer,
)
from apps.projects.constants import RequestStatuses
from apps.projects.models import (
    Direction,
    InvitationToProject,
    ParticipationRequest,
    Project,
    ProjectParticipant,
    ProjectSpecialist,
)

from .constants import PROJECT_PARTICIPATION_REQUEST_ONLY_FIELDS


class DirectionViewSet(ReadOnlyModelViewSet):
    """Представление направлений разработки."""

    queryset = Direction.objects.all()
    serializer_class = DirectionSerializer
    permission_classes = (AllowAny,)


class BaseProjectViewSet(ModelViewSet):
    """Общий viewset для проектов и черновиков."""

    queryset = (
        Project.objects.all()
        .select_related(
            "creator",
            "owner",
        )
        .prefetch_related("favorited_by")
        .order_by("project_status", "-created")
    )

    def get_queryset(self):
        """Общий метод получения queryset-а для проектов и черновиков."""

        queryset = super().get_queryset()
        if self.request.method in SAFE_METHODS:
            queryset = queryset.prefetch_related(
                Prefetch(
                    "project_specialists",
                    queryset=ProjectSpecialist.objects.select_related(
                        "profession"
                    ).prefetch_related("skills"),
                ),
                "directions",
            )
        return self._get_queryset_with_params(queryset, user=self.request.user)


class ProjectViewSet(BaseProjectViewSet):
    """Представление проектов."""

    permission_classes = (IsCreatorOrOwnerOrReadOnly,)
    pagination_class = ProjectPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = ProjectFilter

    def create(self, request, *args, **kwargs):
        """Метод создания проекта, с проверкой на анонимного пользователя."""
        if not request.user.is_authenticated:
            return Response(status=status.HTTP_403_FORBIDDEN)
        return super().create(request, *args, **kwargs)

    def _get_queryset_with_params(self, queryset, user, *args, **kwargs):
        """Метод получения queryset-а c параметрами для проекта."""

        if not isinstance(user, AnonymousUser):
            return queryset.exclude(
                Q(project_status=Project.DRAFT)
                & (~(Q(creator=user) | Q(owner=user)))
            )
        return queryset.exclude(project_status=Project.DRAFT)

    def get_queryset(self):
        """Метод получения отфильтрованного queryset-a с фильтрами."""

        queryset = super().get_queryset()
        queryset = self._get_queryset_with_params(queryset, self.request.user)
        return queryset

    def get_serializer_class(self):
        """Метод получения сериализатора для проектов."""

        if self.request.method in SAFE_METHODS:
            return ReadProjectSerializer
        return WriteProjectSerializer

    def perform_create(self, serializer):
        """
        Метод подготовки данных для процесса предварительного создания проекта.
        """
        serializer.save(
            creator=self.request.user,
            owner=self.request.user,
            project_status=Project.ACTIVE,
        )

    @action(
        ["post", "delete"], permission_classes=(IsAuthenticated,), detail=True
    )
    def favorite(self, request, *args, **kwargs):
        """
        Метод обрабатывает запросы POST и DELETE
        для добавления и удаления проекта из избранного.

        Пример использования:
        POST /projects/<project_id>/favorite/ - добавить проект в избранное.
        DELETE /projects/<project_id>/favorite/ - удалить проект из избранного.
        """
        method = request.method
        user = request.user
        project = self.get_object()
        if method == "POST":
            project.favorited_by.add(user)
            return Response(status=status.HTTP_201_CREATED)
        project.favorited_by.remove(user)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=["delete"],
        permission_classes=(IsCreatorOrOwnerOrReadOnly,),
        detail=True,
        url_path="exclude_participant/(?P<participant_id>d+)",
    )
    def exclude_participant(self, request, participant_id, *args, **kwargs):
        """
        Метод для удаления участника проекта.

        Пример использования:
        DELETE /projects/<project_id>/exclude_participant/<participant_id>/
        - удалить участника из проекта.
        """
        project = self.get_object()
        participant = get_object_or_404(
            ProjectParticipant, id=participant_id, project=project
        )
        participant.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProjectPreviewMainViewSet(mixins.ListModelMixin, GenericViewSet):
    """Представление превью проектов на главной странице."""

    queryset = (
        Project.objects.filter(project_status=Project.ACTIVE)
        .only(
            "id",
            "name",
            "started",
            "ended",
            "directions",
        )
        .prefetch_related(
            Prefetch(
                "project_specialists",
                queryset=ProjectSpecialist.objects.select_related(
                    "profession"
                ),
            ),
            "directions",
        )
    )
    permission_classes = (AllowAny,)
    serializer_class = ProjectPreviewMainSerializer
    pagination_class = ProjectPreviewMainPagination


class DraftViewSet(BaseProjectViewSet):
    """Представление для черновиков проекта."""

    permission_classes = (IsCreatorOrOwner,)

    def get_serializer_class(self):
        """Метод получения сериализатора для черновиков проекта."""

        if self.request.method in SAFE_METHODS:
            return ReadDraftSerializer
        return WriteDraftSerializer

    def _get_queryset_with_params(self, queryset, user, *args, **kwargs):
        """Метод получения queryset-а с параметрами для черновиков проекта."""

        if not isinstance(user, AnonymousUser):
            return queryset.filter(
                Q(project_status=Project.DRAFT)
                & (Q(creator=user) | Q(owner=user))
            )
        return queryset.filter()

    def perform_create(self, serializer):
        """
        Метод подготовки данных для процесса предварительного создания
        черновика проекта.
        """

        return serializer.save(
            creator=self.request.user,
            owner=self.request.user,
            project_status=Project.DRAFT,
        )


class ProjectSpecialistsViewSet(
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    """Представление для специалистов проекта."""

    queryset = ProjectSpecialist.objects.all()
    serializer_class = WriteProjectSpecialistSerializer
    permission_classes = (IsProjectCreatorOrOwner,)


# @extend_schema_view(retrieve=extend_schema(exclude=True),)
# class MyRequestsViewSet(ModelViewSet):
#     """
#     Представление для отображения запросов на участие в проектах,
#     отправленные пользователем, как участником.
#     """

#     queryset = ParticipationRequest.objects.all()
#     permission_classes = (IsAuthenticated,)
#     pagination_class = ProjectPagination
#     http_method_names = ("get", "options")
#     filter_backends = (DjangoFilterBackend,)
#     filterset_class = MyRequestsFilter
#     serializer_class = MyRequestsSerializer

#     def get_queryset(self):
#         """Метод получения отфильтрованного queryset-a с фильтрами."""
#         user = self.request.user
#         queryset = super().get_queryset()
#         return queryset.filter(user=user)


@extend_schema_view(
    retrieve=extend_schema(exclude=True),
)
class ProjectParticipationRequestsViewSet(ModelViewSet):
    """Представление для запросов на участие в проекте."""

    queryset = ParticipationRequest.objects.all()
    permission_classes = (
        IsParticipationRequestCreatorOrProjectCreatorOrOwnerReadOnly,
    )
    http_method_names = ("get", "post", "patch", "delete", "options")
    filter_backends = (DjangoFilterBackend,)
    filterset_class = MyRequestsFilter

    def get_queryset(self) -> QuerySet["ParticipationRequest"]:
        """Метод получения queryset-а для запросов на участие в проекте."""

        queryset = (
            super()
            .get_queryset()
            .select_related(
                "user",
            )
        )
        if self.request.method in SAFE_METHODS:
            queryset = queryset.select_related(
                "project__creator",
                "project__owner",
                "position__profession",
            ).prefetch_related(
                "project__directions",
            )
            user = self.request.user
            if (
                queryset.filter(project__owner=user).exists()
                or queryset.filter(project__creator=user).exists()
            ):
                queryset = queryset.exclude(
                    request_status__in=[
                        RequestStatuses.ACCEPTED,
                        RequestStatuses.REJECTED,
                    ]
                )
                queryset.filter(is_viewed=False).update(is_viewed=True)
                return queryset
        return queryset.filter(Q(user=self.request.user)).only(
            *PROJECT_PARTICIPATION_REQUEST_ONLY_FIELDS.get(self.action, ())
        )

    # Не нужен, так как меняться просмотренное должно в методе ответа,
    # после ответа меняется просмортено или нет
    #
    # def get_object(self) -> ParticipationRequest:
    #     """Метод получения объекта запроса на участие в проекте."""

    #     participation_request = super().get_object()
    #     if (
    #         self.request.method in ("GET")
    #         and not participation_request.is_viewed
    #         and self.request.user
    #         in (
    #             participation_request.project.creator,
    #             participation_request.project.owner,
    #         )
    #     ):
    #         participation_request.is_viewed = True
    #         participation_request.save()
    #     return participation_request

    def get_serializer_class(self) -> type[BaseSerializer]:
        """Метод получения сериализатора для запросов на участие в проекте."""

        is_owner = any(
            self.request.user in (pr.project.owner, pr.project.creator)
            for pr in self.get_queryset()
        )
        if self.request.method in SAFE_METHODS:
            if is_owner:
                return ReadListParticipationRequestSerializer
            return MyRequestsSerializer
        return WriteParticipationRequestSerializer

    def perform_create(self, serializer) -> None:
        """
        Метод предварительного создания объекта запроса на участие в проекте.
        """

        serializer.save(
            user=self.request.user, request_status=RequestStatuses.IN_PROGRESS
        )

    @extend_schema(
        request=WriteParticipationRequestAnswerSerializer,
    )
    @action(
        detail=True,
        methods=["patch"],
        permission_classes=(IsProjectCreatorOrOwnerForParticipationRequest,),
        serializer_class=WriteParticipationRequestAnswerSerializer,
    )
    def answer(self, request, pk) -> Response:
        """Метод ответа на запрос на участие в проекте."""

        participation_request = self.get_object()
        serializer = self.serializer_class(
            instance=participation_request,
            data=request.data,
            context=self.get_serializer_context(),
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class InvitationToProjectViewSet(ModelViewSet):
    """Представление для создания и управления приглашениями в проект"""

    http_method_names = ("get", "post", "patch", "delete", "options")
    permission_classes = (IsInvitationAuthorOrUser,)

    def get_queryset(self):
        user = self.request.user
        return (
            InvitationToProject.objects.filter(Q(user=user) | Q(author=user))
            .order_by("-created")
            .select_related(
                "project",
                "position",
                "user",
                "author",
            )
            .prefetch_related(
                "project__directions",
                "position__profession",
            )
            .only(
                "user",
                "project__name",
                "project__creator",
                "project__owner",
                "position__is_required",
                "position__profession",
                "cover_letter",
                "answer",
                "is_viewed",
                "request_status",
                "created",
                "author",
            )
        )

    def get_serializer_class(self):
        self.request.method in SAFE_METHODS
        # return ReadInvitationToProjectSerializer
        return WriteInvitationToProjectSerializer

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            request_status=RequestStatuses.IN_PROGRESS,
        )

    @extend_schema(
        exclude=True,
    )
    def partial_update(self, request, *args, **kwargs):
        return Response(
            {"detail": "Вы не можете изменить приглашение"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @extend_schema(
        request=PartialWriteInvitationToProjectSerializer,
    )
    @action(
        detail=True,
        methods=[
            "patch",
        ],
        serializer_class=PartialWriteInvitationToProjectSerializer,
    )
    def answer(self, request, *args, **kwargs) -> Response:
        """Метод ответа на запрос на участие в проекте."""

        instance = self.get_object()
        serializer = self.serializer_class(
            instance=instance,
            data=request.data,
            context=self.get_serializer_context(),
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

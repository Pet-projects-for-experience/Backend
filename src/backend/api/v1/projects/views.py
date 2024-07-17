from django.contrib.auth.models import AnonymousUser
from django.db.models import Prefetch, Q, QuerySet
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
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

from api.v1.projects.filters import ProjectFilter
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
    PartialWriteInvitationToProjectSerializer,
    ProjectPreviewMainSerializer,
    ReadDraftSerializer,
    ReadInvitationToProjectSerializer,
    ReadListParticipationRequestSerializer,
    ReadParticipantSerializer,
    ReadProjectSerializer,
    ReadRetrieveParticipationRequestSerializer,
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
        .order_by("status", "-created")
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
                Q(status=Project.DRAFT) & (~(Q(creator=user) | Q(owner=user)))
            )
        return queryset.exclude(status=Project.DRAFT)

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
            status=Project.ACTIVE,
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
            project.is_favorite.add(user)
            return Response(status=status.HTTP_201_CREATED)
        project.is_favorite.remove(user)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProjectPreviewMainViewSet(mixins.ListModelMixin, GenericViewSet):
    """Представление превью проектов на главной странице."""

    queryset = (
        Project.objects.filter(status=Project.ACTIVE)
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
                Q(status=Project.DRAFT) & (Q(creator=user) | Q(owner=user))
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
            status=Project.DRAFT,
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


class ProjectParticipationRequestsViewSet(ModelViewSet):
    """Представление для запросов на участие в проекте."""

    queryset = ParticipationRequest.objects.all()
    permission_classes = (
        IsParticipationRequestCreatorOrProjectCreatorOrOwnerReadOnly,
    )
    http_method_names = ("get", "post", "patch", "delete", "options")

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
            if self.action == "retrieve":
                queryset = queryset.prefetch_related(
                    "position__skills",
                )
        return queryset.filter(
            Q(user=self.request.user)
            | (
                Q(project__owner=self.request.user)
                | Q(project__creator=self.request.user)
            )
        ).only(*PROJECT_PARTICIPATION_REQUEST_ONLY_FIELDS.get(self.action, ()))

    def get_object(self) -> ParticipationRequest:
        """Метод получения объекта запроса на участие в проекте."""

        participation_request = super().get_object()
        if (
            self.request.method in ("GET", "PATCH")
            and not participation_request.is_viewed
            and self.request.user
            in (
                participation_request.project.creator,
                participation_request.project.owner,
            )
        ):
            participation_request.is_viewed = True
            participation_request.save()
        return participation_request

    def get_serializer_class(self) -> type[BaseSerializer]:
        """Метод получения сериализатора для запросов на участие в проекте."""

        if self.request.method in SAFE_METHODS:
            if self.action != "list":
                return ReadRetrieveParticipationRequestSerializer
            return ReadListParticipationRequestSerializer
        return WriteParticipationRequestSerializer

    def perform_create(self, serializer) -> None:
        """
        Метод предварительного создания объекта запроса на участие в проекте.
        """

        serializer.save(
            user=self.request.user, status=RequestStatuses.IN_PROGRESS
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


class ParticipantsViewSet(
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    """Представление для участников проекта."""

    queryset = ProjectParticipant.objects.all()
    serializer_class = ReadParticipantSerializer
    # permission_classes = (IsAuthenticated,)
    pagination_class = None
    http_method_names = ("get", "delete", "options")

    def get_queryset(self) -> QuerySet["ProjectParticipant"]:
        """Метод получения queryset-а для участников проекта."""

        queryset = (
            super()
            .get_queryset()
            .filter(
                project=self.kwargs.get("project_pk"),
            )
        )

        if self.request.method == "GET":
            queryset = (
                queryset.select_related("user__profile", "profession")
                .prefetch_related("skills")
                .only(
                    "user__profile__user_id",
                    "user__profile__avatar",
                    "profession",
                    "skills",
                )
            )
        return queryset


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
                "status",
                "created",
                "author",
            )
        )

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return ReadInvitationToProjectSerializer
        return WriteInvitationToProjectSerializer

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user, status=RequestStatuses.IN_PROGRESS
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

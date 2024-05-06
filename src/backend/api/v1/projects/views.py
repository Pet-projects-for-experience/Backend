from django.contrib.auth.models import AnonymousUser
from django.db.models import Prefetch, Q
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import (
    GenericViewSet,
    ModelViewSet,
    ReadOnlyModelViewSet,
)

from api.v1.projects.paginations import (
    ProjectPagination,
    ProjectPreviewMainPagination,
)
from api.v1.projects.permissions import (
    IsCreatorOrOwner,
    IsCreatorOrOwnerOrReadOnly,
    IsParticipationRequestCreatorOrProjectCreatorOrOwnerReadOnly,
    IsProjectCreatorOrOwner,
)
from api.v1.projects.serializers import (
    DirectionSerializer,
    ProjectPreviewMainSerializer,
    ReadDraftSerializer,
    ReadParticipationRequestSerializer,
    ReadProjectSerializer,
    WriteDraftSerializer,
    WriteParticipationRequestAnswerSerializer,
    WriteParticipationRequestSerializer,
    WriteProjectSerializer,
    WriteProjectSpecialistSerializer,
)
from apps.projects.models import (
    Direction,
    ParticipationRequest,
    Project,
    ProjectSpecialist,
)


class DirectionViewSet(ReadOnlyModelViewSet):
    """Представление направлений разработки."""

    queryset = Direction.objects.all()
    serializer_class = DirectionSerializer
    permission_classes = (IsAuthenticated,)


class BaseProjectViewSet(ModelViewSet):
    """Общий viewset для проектов и черновиков."""

    queryset = (
        Project.objects.all()
        .select_related(
            "creator",
            "owner",
        )
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

    def _get_queryset_with_params(self, queryset, user, *args, **kwargs):
        """Метод получения queryset-а c параметрами для проекта."""

        if not isinstance(user, AnonymousUser):
            return queryset.exclude(
                Q(status=Project.DRAFT) & (~(Q(creator=user) | Q(owner=user)))
            )
        return queryset.exclude(status=Project.DRAFT)

    def get_serializer_class(self):
        """Метод получения сериализатора для проектов."""

        if self.request.method in SAFE_METHODS:
            return ReadProjectSerializer
        return WriteProjectSerializer

    def perform_create(self, serializer):
        """
        Метод подготовки данных для процесса предварительного создания проекта.
        """

        return serializer.save(
            creator=self.request.user,
            owner=self.request.user,
            status=Project.ACTIVE,
        )


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

    queryset = ParticipationRequest.objects.all().select_related("user")
    permission_classes = (
        IsParticipationRequestCreatorOrProjectCreatorOrOwnerReadOnly,
    )
    http_method_names = ("get", "post", "patch", "delete", "options")

    def get_queryset(self):
        """Метод получения queryset-а для запросов на участие в проекте."""

        queryset = super().get_queryset()
        if self.request.method != "DELETE":
            queryset = (
                queryset.select_related(
                    "project",
                    "project__creator",
                    "project__owner",
                    "position__profession",
                )
                .prefetch_related(
                    "project__directions",
                )
                .only(
                    "user",
                    "project__name",
                    "project__creator",
                    "project__owner",
                    "position__is_required",
                    "position__profession",
                    "status",
                    "is_viewed",
                    "cover_letter",
                    "answer",
                    "created",
                )
            )
        return queryset.filter(
            Q(user=self.request.user)
            | (
                Q(project__owner=self.request.user)
                | Q(project__creator=self.request.user)
            )
        )

    def get_object(self):
        """Метод получения объекта запроса на участие в проекте."""
        participation_request = super().get_object()
        if (
            self.request.method in SAFE_METHODS
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

    def get_serializer_class(self):
        """Метод получения сериализатора для запросов на участие в проекте."""

        if self.request.method in SAFE_METHODS:
            return ReadParticipationRequestSerializer
        return WriteParticipationRequestSerializer

    def perform_create(self, serializer):
        """
        Метод предварительного создания объекта запроса на участие в проекте.
        """

        serializer.save(
            user=self.request.user,
            status=ParticipationRequest.RequestStatuses.IN_PROGRESS,
        )

    @action(
        detail=True,
        methods=["patch"],
        permission_classes=(IsProjectCreatorOrOwner,),
        serializer_class=WriteParticipationRequestAnswerSerializer,
    )
    def answer(self, request, pk):
        """Метод ответа на запрос на участие в проекте."""

        participation_request = self.get_object()
        serializer = self.serializer_class(
            instance=participation_request, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

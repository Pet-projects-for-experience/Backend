from django.contrib.auth.models import AnonymousUser
from django.db.models import Prefetch, Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins
from rest_framework.permissions import SAFE_METHODS, AllowAny, IsAuthenticated
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
)
from api.v1.projects.serializers import (
    DirectionSerializer,
    ProjectPreviewMainSerializer,
    ReadDraftSerializer,
    ReadProjectSerializer,
    WriteDraftSerializer,
    WriteProjectSerializer,
)
from apps.projects.models import Direction, Project, ProjectSpecialist


class DirectionViewSet(ReadOnlyModelViewSet):
    """Представление направлений разработки."""

    queryset = Direction.objects.all()
    serializer_class = DirectionSerializer
    permission_classes = (IsAuthenticated,)


class BaseProjectViewSet:
    """Общий viewset для проектов и черновиков."""

    queryset = (
        Project.objects.select_related("creator", "owner")
        .prefetch_related(
            Prefetch(
                "project_specialists",
                queryset=ProjectSpecialist.objects.select_related(
                    "specialist"
                ).prefetch_related("skills"),
            ),
            "directions",
        )
        .order_by("status", "-created")
    )

    def get_queryset(self):
        """Общий метод получения queryset-а для проектов и черновиков."""

        queryset = super().get_queryset()
        return self._get_queryset_with_params(queryset, user=self.request.user)

    def perform_create(self, serializer):
        """
        Общий метод предварительного создания объекта проекта или черновика.
        """

        serializer.save(**self._get_perform_create_data())


class ProjectViewSet(BaseProjectViewSet, ModelViewSet):
    """Представление проектов."""

    permission_classes = (IsCreatorOrOwnerOrReadOnly,)
    pagination_class = ProjectPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = ProjectFilter

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
        queryset = self.filter_queryset(queryset)
        return queryset

    def get_serializer_class(self):
        """Метод получения сериализатора для проектов."""

        if self.request.method in SAFE_METHODS:
            return ReadProjectSerializer
        return WriteProjectSerializer

    def _get_perform_create_data(self):
        """
        Метод подготовки данных для процесса предварительного создания проекта.
        """

        return {
            "creator": self.request.user,
            "owner": self.request.user,
        }


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
                    "specialist"
                ),
            ),
            "directions",
        )
    )
    permission_classes = (AllowAny,)
    serializer_class = ProjectPreviewMainSerializer
    pagination_class = ProjectPreviewMainPagination


class DraftViewSet(BaseProjectViewSet, ModelViewSet):
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

    def _get_perform_create_data(self):
        """
        Метод подготовки данных для процесса предварительного создания проекта.
        """

        return {
            "creator": self.request.user,
            "owner": self.request.user,
            "status": Project.DRAFT,
        }

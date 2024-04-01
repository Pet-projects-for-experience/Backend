from django.db.models import Prefetch, Q
from rest_framework import mixins
from rest_framework.permissions import (
    SAFE_METHODS,
    AllowAny,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.viewsets import (
    GenericViewSet,
    ModelViewSet,
    ReadOnlyModelViewSet,
)

from api.v1.projects.paginations import (
    ProjectPagination,
    ProjectPreviewMainPagination,
)
from api.v1.projects.permissions import IsCreatorOrOwnerOrReadOnly
from api.v1.projects.serializers import (
    DirectionSerializer,
    DraftSerializer,
    ProjectPreviewMainSerializer,
    ReadProjectSerializer,
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
        .order_by("-status", "-created")
    )

    def get_queryset(self):
        """Общий метод получения queryset-а для проектов и черновиков."""

        queryset = super().get_queryset()
        if self.request.user.is_anonymous:
            return self._get_queryset_with_params(queryset, anonymous=True)
        return self._get_queryset_with_params(queryset, anonymous=False)

    def perform_create(self, serializer):
        """
        Общий метод предварительного создания объекта проекта или черновика.
        """

        serializer.save(**self._get_perform_create_data())


class ProjectViewSet(BaseProjectViewSet, ModelViewSet):
    """Представление проектов."""

    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = ProjectPagination

    def _get_queryset_with_params(self, queryset, *args, **kwargs):
        """Метод получения queryset-а c параметрами для проекта."""

        if kwargs.get("anonymous", False):
            return queryset.exclude(status=Project.DRAFT)
        return queryset.exclude(
            Q(status=Project.DRAFT)
            & (~(Q(creator=self.request.user) | Q(owner=self.request.user)))
        )

    def get_serializer_class(self):
        """Метод получения сериализатора проектов."""

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
        Project.objects.exclude(status=Project.DRAFT)
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

    permission_classes = (IsCreatorOrOwnerOrReadOnly,)
    serializer_class = DraftSerializer

    def _get_queryset_with_params(self, queryset, *args, **kwargs):
        """Метод получения queryset-а с параметрами для черновиков проекта."""

        if kwargs.get("anonymous", False):
            return queryset.filter()
        return queryset.filter(
            Q(creator=self.request.user) | Q(owner=self.request.user)
        )

    def _get_perform_create_data(self):
        """
        Метод подготовки данных для процесса предварительного создания проекта.
        """

        return {
            "creator": self.request.user,
            "owner": self.request.user,
            "status": Project.DRAFT,
        }

from http import HTTPStatus

from django.contrib.auth.models import AnonymousUser
from django.db.models import Prefetch, Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, AllowAny, IsAuthenticated
from rest_framework.response import Response
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
    IsProjectCreatorOrOwner,
)
from api.v1.projects.serializers import (
    DirectionSerializer,
    ProjectPreviewMainSerializer,
    ReadDraftSerializer,
    ReadProjectSerializer,
    WriteDraftSerializer,
    WriteProjectSerializer,
    WriteProjectSpecialistSerializer,
)
from apps.projects.models import Direction, Project, ProjectSpecialist


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
        .prefetch_related("is_favorite")
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

        return serializer.save(
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
            return Response(status=HTTPStatus.CREATED)
        return Response(status=HTTPStatus.NO_CONTENT)


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
        Метод подготовки данных для процесса предварительного создания проекта.
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

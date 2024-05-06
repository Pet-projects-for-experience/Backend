from django.db.models import Prefetch
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import (
    CreateModelMixin,
    DestroyModelMixin,
    UpdateModelMixin,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ReadOnlyModelViewSet

from apps.profile.models import Profile, Specialist

from .paginations import ProfilesPagination
from .serializers import (
    ProfileDetailReadSerializer,
    ProfileMeReadSerializer,
    ProfileMeWriteSerializer,
    ProfilePreviewReadSerializer,
    SpecialistWriteSerializer,
)

USER_FIELDS_TO_DEFER = (
    "user__email",
    "user__modified",
    "user__is_active",
    "user__password",
    "user__last_login",
    "user__is_superuser",
    "user__is_staff",
    "user__is_organizer",
)


class ProfilesViewSet(ReadOnlyModelViewSet):
    """Представление профилей специалистов."""

    lookup_field = "user_id"
    pagination_class = ProfilesPagination
    queryset = (
        Profile.objects.select_related("user")
        .prefetch_related(
            Prefetch(
                "specialists",
                queryset=(
                    Specialist.objects.select_related(
                        "profession"
                    ).prefetch_related("skills")
                ),
            )
        )
        .order_by("-user__created")
    )

    def get_serializer_class(self):
        """Получение сериализатора для профилей."""

        if self.action == "retrieve":
            return ProfileDetailReadSerializer
        if self.action == "me":
            if self.request.method == "PATCH":
                return ProfileMeWriteSerializer
            return ProfileMeReadSerializer
        return ProfilePreviewReadSerializer

    def get_visible_profiles(self):
        """Извлечение профилей, доступных другим пользователям."""

        user = self.request.user
        if user.is_authenticated and user.is_organizer:
            return self.queryset.exclude(
                visible_status=Profile.VisibilitySettings.NOBODY
            )
        return self.queryset.filter(
            visible_status=Profile.VisibilitySettings.ALL
        )

    def get_queryset(self):
        """Получение queryset-а профилей."""

        if self.action == "list":
            return self.get_visible_profiles().only(
                "user_id",
                "avatar",
                "user__username",
                "name",
                "ready_to_participate",
            )

        if self.action == "retrieve":
            return self.get_visible_profiles().defer(*USER_FIELDS_TO_DEFER)

        return super().get_queryset()

    @action(
        methods=["get", "patch"],
        detail=False,
        permission_classes=[IsAuthenticated],
    )
    def me(self, request):
        """Просмотр и редактирование профиля его владельцем."""

        try:
            profile = (
                self.get_queryset()
                .defer(*USER_FIELDS_TO_DEFER)
                .get(user=request.user)
            )
        except Profile.DoesNotExist:
            return Response(status.HTTP_404_NOT_FOUND)

        if request.method == "GET":
            return Response(
                self.get_serializer_class()(profile).data, status.HTTP_200_OK
            )

        if request.method == "PATCH":
            serializer = self.get_serializer_class()(
                profile, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status.HTTP_200_OK)


class SpecialistsViewSet(
    CreateModelMixin, UpdateModelMixin, DestroyModelMixin, GenericViewSet
):
    """Представление специальностей в профиле пользователя-владельца."""

    serializer_class = SpecialistWriteSerializer
    permission_classes = [IsAuthenticated]
    lookup_url_kwarg = "specialist_id"
    http_method_names = ["post", "patch", "delete", "options", "head"]

    def get_profile(self):
        """Извлечение профиля пользователя."""

        try:
            profile = Profile.objects.only("pk").get(user=self.request.user)
        except Profile.DoesNotExist:
            return Response(status.HTTP_404_NOT_FOUND)
        return profile

    def get_queryset(self):
        """Получение queryset-а специализаций профиля пользователя."""

        return (
            Specialist.objects.select_related("profession")
            .prefetch_related("skills")
            .filter(profile=self.get_profile())
        )

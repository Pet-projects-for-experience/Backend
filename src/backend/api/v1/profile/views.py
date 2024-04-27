from django.db.models import Prefetch
from drf_spectacular.utils import extend_schema
from rest_framework.mixins import (
    CreateModelMixin,
    DestroyModelMixin,
    UpdateModelMixin,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
)
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from apps.profile.constants import MAX_PROFILE_PROFESSIONS
from apps.profile.models import Profile, Specialist

from .serializers import (
    ProfileReadSerializer,
    ProfileWriteSerializer,
    SpecialistWriteSerializer,
)

USER_FIELDS_TO_DEFER = (
    "user__password",
    "user__last_login",
    "user__is_superuser",
    "user__is_staff",
    "user__is_organizer",
)


class ProfileView(APIView):
    """Чтение, частичное изменение профиля его владельцем."""

    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: ProfileReadSerializer})
    def get(self, request):
        """Просмотр профиля его владельцем."""
        try:
            profile = (
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
                .defer(*USER_FIELDS_TO_DEFER)
                .get(user=request.user)
            )
        except Profile.DoesNotExist:
            return Response(HTTP_404_NOT_FOUND)
        return Response(
            data=ProfileReadSerializer(profile).data, status=HTTP_200_OK
        )

    @extend_schema(
        request=ProfileWriteSerializer,
        responses={200: ProfileWriteSerializer},
    )
    def patch(self, request):
        """
        Редактирование профиля, в том числе настроек видимости.
        Доступно только авторизованному пользователю-владельцу.
        """
        serializer = ProfileWriteSerializer(
            request.user.profile, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, HTTP_200_OK)


class ProfileSpecialistsViewSet(
    CreateModelMixin, UpdateModelMixin, DestroyModelMixin, GenericViewSet
):
    """Представление специальностей в профиле пользователя-владельца."""

    serializer_class = SpecialistWriteSerializer
    permission_classes = [IsAuthenticated]
    lookup_url_kwarg = "specialist_id"
    http_method_names = ["post", "patch", "delete"]

    def get_profile(self):
        try:
            profile = Profile.objects.only("pk").get(user=self.request.user)
        except Profile.DoesNotExist:
            return Response(HTTP_400_BAD_REQUEST)
        return profile

    def get_queryset(self):
        return (
            Specialist.objects.select_related("profession")
            .prefetch_related("skills")
            .filter(profile=self.get_profile())
        )

    def create(self, request, *args, **kwargs):
        profile = self.get_profile()
        if profile.specialists.count() == MAX_PROFILE_PROFESSIONS:
            raise ValidationError(
                "Можно добавить не более "
                f"{MAX_PROFILE_PROFESSIONS} специальностей"
            )
        return super().create(request, *args, **kwargs)

from django.db.models import Prefetch
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_404_NOT_FOUND
from rest_framework.views import APIView

from apps.profile.models import Profile, Specialist
from .serializers import (
    SettingProfileSerializer,
)

USER_FIELDS_TO_DEFER = [
    "user__password",
    "user__is_superuser",
    "user__is_staff",
    "user__is_active",
    "user__last_login",
    "user__created",
    "user__modified",
    "user__is_organizer",
    "user__email"
]


class SettingProfileView(APIView):
    """Чтение, частичное изменение профиля."""

    permission_classes = [IsAuthenticated]
    serializer_class = SettingProfileSerializer

    def get_profile(self):
        """
        Получить объект профиля и связанные с ним
        объекты специалиста с необходимыми полями.
        """
        profiles = Profile.objects.filter(
            user=self.request.user
        ).select_related("user").prefetch_related(
            Prefetch(
                "professions",
                queryset=Specialist.objects.select_related(
                    "profession"
                ).prefetch_related("skills").defer(
                    "skills__name"
                )
            )
        ).defer(*USER_FIELDS_TO_DEFER)
        if not profiles:
            return Response(HTTP_404_NOT_FOUND)
        return profiles[0]

    @extend_schema(responses={200: serializer_class})
    def get(self, request):
        """Просмотр профиля его владельцем."""
        return Response(
            data=self.serializer_class(self.get_profile()).data,
            status=HTTP_200_OK
        )

    @extend_schema(responses={200: serializer_class})
    def patch(self, request):
        """
        Редактирование профиля, в том числе настроек видимости.
        Доступно только авторизованному пользователю-владельцу.
        """
        serializer = self.serializer_class(
            self.get_profile(),
            data=request.data,
            context={"request": request},
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, HTTP_200_OK)

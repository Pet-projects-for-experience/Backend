from rest_framework import generics, viewsets

from api.v1.profile.permissions import IsOwnerOrReadOnly
from api.v1.profile.serializers import (
    ProfileSerializer,
    ProfileUpdateSerializer,
    ProfileVisibilitySerializer,
)
from apps.profile.models import Profile


class ProfileUpdateView(generics.RetrieveUpdateAPIView):
    """Представление на редактирование профиля"""

    queryset = Profile.objects.prefetch_related("userskills").prefetch_related(
        "userspecialization"
    )
    serializer_class = ProfileUpdateSerializer
    permission_classes = [
        IsOwnerOrReadOnly,
    ]


class ProfileViewSet(viewsets.ReadOnlyModelViewSet):
    """Представление на просмотр профиля в зависимости от настроек видимости"""

    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = Profile.objects.all()
        is_organizer = user.is_authenticated and user.is_organizer
        if is_organizer:
            queryset = queryset.filter(
                visible_status__in=[Profile.ALL, Profile.CREATOR_ONLY]
            )
        else:
            queryset = queryset.filter(visible_status=Profile.ALL)

        return queryset


class ProfileVisibilityView(generics.RetrieveUpdateAPIView):
    """Представление на редактирование видимости профиля"""

    queryset = Profile.objects.all()
    serializer_class = ProfileVisibilitySerializer
    permission_classes = [
        IsOwnerOrReadOnly,
    ]

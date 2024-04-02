from rest_framework import generics

from api.v1.profile.permissions import IsOwnerOrReadOnly
from api.v1.profile.serializers import (
    ProfileSerializer,
    ProfileUpdateSerializer,
)
from apps.profile.models import Profile


class ProfileView(generics.UpdateAPIView):
    """Представление на изменение данных в профиле"""

    queryset = Profile.objects.all()
    serializer_class = ProfileUpdateSerializer
    permission_classes = [IsOwnerOrReadOnly]


class ProfileListAPIView(generics.ListAPIView):
    """Список профилей в зависимости от их видимости"""

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

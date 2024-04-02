from django.db import connection
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.v1.general.serializers import (
    SectionSerializer,
    SkillSerializer,
    SpecialistSerializer,
)
from apps.general.models import Section, Skill, Specialist


class SectionViewSet(viewsets.ReadOnlyModelViewSet):
    """Текстовая секция на странице"""

    queryset = Section.objects.all()
    serializer_class = SectionSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["page_id"]


class CounterApiView(generics.RetrieveAPIView):
    """Счетчик проектов и пользователей"""

    @method_decorator(cache_page(600))
    def get(self, request):
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT count(*) from projects_project union all SELECT count(*)
                from users_user
                """
            )
            row = cursor.fetchall()
        return Response({"projects": row[0][0], "users": row[1][0]})


class SpecialistViewSet(viewsets.ReadOnlyModelViewSet):
    """Представление специальностей."""

    queryset = Specialist.objects.all()
    serializer_class = SpecialistSerializer
    permission_classes = (IsAuthenticated,)


class SkillViewSet(viewsets.ReadOnlyModelViewSet):
    """Представление специальностей."""

    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    permission_classes = (IsAuthenticated,)

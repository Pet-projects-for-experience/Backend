from django.db import connection
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from api.v1.general.serializers import (
    ProfessionSerializer,
    SectionSerializer,
    SkillSerializer,
)
from apps.general.models import Profession, Section, Skill


class SectionViewSet(viewsets.ReadOnlyModelViewSet):
    """Представление информационных секций для страниц сайта."""

    queryset = Section.objects.all()
    serializer_class = SectionSerializer
    permission_classes = (AllowAny,)
    pagination_class = None
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["page_id"]


class CounterApiView(generics.RetrieveAPIView):
    """Представление счетчика проектов и пользователей."""

    @method_decorator(cache_page(600))
    def get(self, request) -> Response:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT count(*) from projects_project union all SELECT count(*)
                from users_user
                """
            )
            row = cursor.fetchall()
        return Response({"projects": row[0][0], "users": row[1][0]})


class ProfessionViewSet(viewsets.ReadOnlyModelViewSet):
    """Представление профессий."""

    queryset = Profession.objects.all()
    serializer_class = ProfessionSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class SkillViewSet(viewsets.ReadOnlyModelViewSet):
    """Представление навыков."""

    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    permission_classes = (AllowAny,)
    pagination_class = None

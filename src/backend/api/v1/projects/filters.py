from django.contrib.postgres.search import SearchQuery, SearchVector
from django.db.models import Q
from django_filters.rest_framework import FilterSet, filters
from langdetect import detect

from apps.general.constants import LEVEL_CHOICES
from apps.general.models import Profession, Skill
from apps.projects.constants import BUSYNESS_CHOICES, PROJECT_STATUS_CHOICES
from apps.projects.models import Direction, Project


class ProjectFilter(FilterSet):
    """Класс фильтрации проектов, по запросу на главной странице."""

    status = filters.MultipleChoiceFilter(choices=PROJECT_STATUS_CHOICES)
    started = filters.DateFromToRangeFilter()
    ended = filters.DateFromToRangeFilter()
    recruitment_status = filters.NumberFilter(
        method="filter_recruitment_status",
    )
    specialization = filters.ModelMultipleChoiceFilter(
        field_name="project_specialists__profession",
        queryset=Profession.objects.all(),
    )
    skill = filters.ModelMultipleChoiceFilter(
        field_name="project_specialists__skills", queryset=Skill.objects.all()
    )
    level = filters.MultipleChoiceFilter(
        field_name="project_specialists__level", choices=LEVEL_CHOICES
    )
    busyness = filters.MultipleChoiceFilter(choices=BUSYNESS_CHOICES)
    directions = filters.ModelMultipleChoiceFilter(
        field_name="directions", queryset=Direction.objects.all()
    )
    project_role = filters.NumberFilter(method="get_project_role")
    search = filters.CharFilter(method="project_search")
    is_favorite = filters.NumberFilter(method="filter_is_favorite_project")

    class Meta:
        model = Project
        fields = (
            "status",
            "started",
            "ended",
            "recruitment_status",
            "specialization",
            "skill",
            "level",
            "busyness",
            "directions",
            "search",
        )

    def filter_recruitment_status(self, queryset, name, value):
        if value == 1:
            return queryset.exclude(
                Q(project_specialists__is_required=False)
                | Q(project_specialists=None)
            )
        elif value == 0:
            return queryset.filter(
                ~Q(project_specialists__is_required=True)
                | Q(project_specialists=None)
            )
        return queryset

    def get_project_role(self, queryset, name, value):
        user = self.request.user
        if value == 1:
            return queryset.filter(Q(owner=user) | Q(creator=user))
        elif value == 0:
            return queryset.filter(participants=user).exclude(
                status=Project.DRAFT
            )
        return queryset

    def project_search(self, queryset, name, value):
        if value:
            search_language = detect(value)
            if search_language == "ru":
                search_query = SearchQuery(value, config="russian")
                vector = SearchVector("name", "description", config="russian")
            elif search_language == "en":
                search_query = SearchQuery(value, config="english")
                vector = SearchVector("name", "description", config="english")
            else:
                search_query = SearchQuery(value)
                vector = SearchVector("name", "description")
            return queryset.annotate(search=vector).filter(search=search_query)
        return queryset

    def filter_is_favorite_project(self, queryset, name, value):
        user = self.request.user
        if value == 1 and user.is_authenticated:
            return queryset.filter(favorited_by=user)
        return queryset

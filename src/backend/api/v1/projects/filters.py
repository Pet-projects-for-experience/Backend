from django.db.models import Q
from django_filters.rest_framework import FilterSet, filters

from apps.general.constants import LEVEL_CHOICES
from apps.projects.constants import BUSYNESS_CHOICES, PROJECT_STATUS_CHOICES
from apps.projects.models import Project


class ProjectFilter(FilterSet):
    """Класс фильтрации проектов, по запросу на главной странице."""

    status = filters.MultipleChoiceFilter(choices=PROJECT_STATUS_CHOICES)
    started = filters.DateFromToRangeFilter()
    ended = filters.DateFromToRangeFilter()
    recruitment_status = filters.NumberFilter(
        method="filter_recruitment_status",
    )
    specialization = filters.NumberFilter(
        field_name="project_specialists__specialist"
    )
    skill = filters.NumberFilter(field_name="project_specialists__skills")
    level = filters.MultipleChoiceFilter(choices=LEVEL_CHOICES)
    busyness = filters.MultipleChoiceFilter(choices=BUSYNESS_CHOICES)
    direction = filters.NumberFilter(field_name="direction")

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
            "direction",
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

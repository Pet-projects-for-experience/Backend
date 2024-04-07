from django_filters.rest_framework import FilterSet, filters

from apps.general.constants import LEVEL_CHOICES
from apps.projects.constants import BUSYNESS_CHOICES, STATUS_CHOICES
from apps.projects.models import Project


class ProjectFilter(FilterSet):
    """Класс фильтрации проектов, по запросу на главной странице."""

    status = filters.MultipleChoiceFilter(choices=STATUS_CHOICES)
    started = filters.DateFilter(lookup_expr="gte")
    ended = filters.DateFromToRangeFilter(lookup_expr="lte")
    recruitment_status = filters.MultipleChoiceFilter(
        choices=(
            ("open", "Набор открыт"),
            ("closed", "Набор закрыт"),
        )
    )
    specialization = filters.CharFilter(
        field_name="project_specialists__specialist__specialization"
    )
    skill = filters.CharFilter(field_name="project_specialists__skills__name")
    level = filters.MultipleChoiceFilter(choices=LEVEL_CHOICES)
    busyness = filters.MultipleChoiceFilter(choices=BUSYNESS_CHOICES)
    direction = filters.CharFilter(field_name="direction__name")

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

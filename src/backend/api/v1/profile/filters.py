from django_filters.rest_framework import FilterSet, filters

from apps.general.constants import LEVEL_CHOICES
from apps.profile.models import Profile


class ProfileFilter(FilterSet):
    """Класс фильтрации специалистов, по запросу на главной странице."""

    ready_to_participate = filters.BooleanFilter()
    level = filters.MultipleChoiceFilter(choices=LEVEL_CHOICES)
    specialization = filters.NumberFilter(
        field_name="userspecialization__specialization"
    )
    skills = filters.NumberFilter(field_name="userskills__skill")

    class Meta:
        model = Profile
        fields = (
            "ready_to_participate",
            "level",
            "specialization",
            "skills",
        )

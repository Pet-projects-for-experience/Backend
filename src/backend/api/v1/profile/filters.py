from django_filters.rest_framework import FilterSet, filters

from apps.general.constants import LEVEL_CHOICES
from apps.general.models import Profession, Skill
from apps.profile.models import Profile


class ProfileFilter(FilterSet):
    """Класс фильтрации профилей специалистов."""

    ready_to_participate = filters.BooleanFilter()
    level = filters.MultipleChoiceFilter(
        field_name="specialists__level", choices=LEVEL_CHOICES
    )
    specialization = filters.ModelMultipleChoiceFilter(
        field_name="specialists__profession", queryset=Profession.objects.all()
    )
    skills = filters.ModelMultipleChoiceFilter(
        field_name="specialists__skills", queryset=Skill.objects.all()
    )
    is_favorite = filters.NumberFilter(method="filter_is_favorite_profile")

    class Meta:
        model = Profile
        fields = (
            "ready_to_participate",
            "level",
            "specialization",
            "skills",
            "is_favorite",
        )

    def filter_is_favorite_profile(self, queryset, name, value):
        user = self.request.user
        if user.is_authenticated and value == 1:
            return queryset.filter(favorited_by=user)
        return queryset

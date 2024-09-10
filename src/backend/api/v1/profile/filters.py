from django.db.models import Case, IntegerField, Q, Value, When
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
    search = filters.CharFilter(method="filter_search")

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

    def filter_search(self, queryset, name, value):
        value = value.strip()
        if not value and len(value) < 3:
            return queryset

        exact_match = Q(name__iexact=value) | Q(user__username__iexact=value)
        partial_match = Q(name__icontains=value) | Q(
            user__username__icontains=value
        )

        exact_match_case = When(exact_match, then=Value(0))
        partial_match_case = When(partial_match, then=Value(1))

        queryset = (
            queryset.annotate(
                match_priority=Case(
                    exact_match_case,
                    partial_match_case,
                    default=Value(2),
                    output_field=IntegerField(),
                )
            )
            .filter(exact_match | partial_match)
            .order_by("match_priority", "user_id")
        )

        return queryset

from django.contrib.postgres.search import TrigramSimilarity
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
    user_search = filters.CharFilter(method="user_filter_search")

    class Meta:
        model = Profile
        fields = (
            "ready_to_participate",
            "level",
            "specialization",
            "skills",
            "is_favorite",
            "user_search",
        )

    def filter_is_favorite_profile(self, queryset, name, value):
        user = self.request.user
        if user.is_authenticated and value == 1:
            return queryset.filter(favorited_by=user)
        return queryset

    def user_filter_search(self, queryset, name, value):
        if value and len(value) > 2:
            trigram_similarity = TrigramSimilarity(
                "name", value
            ) + TrigramSimilarity("user__username", value)

            annotated_queryset = queryset.annotate(
                similarity=trigram_similarity
            )

            # Нужно поиграться со значением similarity__gte,
            # это совпадение в процентах, а не в символах
            # GPT рекомендует 0.1.
            # Тестово оставил 0.05 для удобства тестирования на небольшой базе
            return annotated_queryset.filter(similarity__gte=0.05).order_by(
                "-similarity"
            )

        return queryset

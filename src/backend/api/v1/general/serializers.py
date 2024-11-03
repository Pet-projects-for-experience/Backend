from rest_framework import serializers

from api.v1.general.mixins import OverridedFieldMappingMixin
from apps.general.models import Profession, Section, Skill


class CustomModelSerializer(
    OverridedFieldMappingMixin,
    serializers.ModelSerializer,
):
    """
    Модифицированный сериализатор модели с измененным атрибутом сопоставления
    полей модели.
    """

    pass


class SectionSerializer(CustomModelSerializer):
    """Сериализатор информационной секции для страниц сайта."""

    class Meta:
        model = Section
        fields = "__all__"


class ProfessionSerializer(CustomModelSerializer):
    """Сериализатор профессии."""

    class Meta:
        model = Profession
        fields = (
            "speciality",
            "specialization",
        )


class SkillSerializer(CustomModelSerializer):
    """Сериализатор навыков."""

    class Meta:
        model = Skill
        fields = "__all__"

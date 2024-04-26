from rest_framework import serializers

from apps.general.models import Profession, Section, Skill


class SectionSerializer(serializers.ModelSerializer):
    """Сериализатор информационной секции для страниц сайта."""

    class Meta:
        model = Section
        fields = "__all__"


class ProfessionSerializer(serializers.ModelSerializer):
    """Сериализатор профессии."""

    class Meta:
        model = Profession
        fields = "__all__"


class SkillSerializer(serializers.ModelSerializer):
    """Сериализатор навыков."""

    class Meta:
        model = Skill
        fields = "__all__"

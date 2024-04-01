from datetime import date
from typing import Any, Dict

from django.db import transaction
from rest_framework import serializers

from apps.projects.models import Project, ProjectSpecialist


class RecruitmentStatusMixin:
    def calculate_recruitment_status(self, obj):
        """Метод определения статуса набора в проект."""

        if any(
            specialist.is_required
            for specialist in obj.project_specialists.all()
        ):
            return "Набор открыт"
        return "Набор закрыт"


class ProjectOrDraftValidateMixin:
    """Миксин валидации данных проекта или его черновика."""

    def _validate_date(self, value, field_name) -> date:
        """Метод валидации даты."""

        if value < date.today():
            raise serializers.ValidationError(
                f"Дата {field_name} не может быть в прошлом."
            )
        return value

    def validate_started(self, value) -> date:
        """Метод валидации даты начала проекта."""

        return self._validate_date(value, "начала проекта")

    def validate_ended(self, value) -> date:
        """Метод валидации даты завершения проекта."""

        return self._validate_date(value, "завершения проекта")

    def validate(self, attrs) -> Dict[str, Any]:
        """Метод валидации данных проекта или черновика."""

        errors: Dict = {}

        queryset = Project.objects.filter(
            name=attrs.get("name"),
            creator=self.context.get("request").user,  # type: ignore
        )

        if queryset.exists():
            errors.setdefault("unique", []).append(
                "У вас уже есть проект или его черновик с таким названием."
            )
        started = attrs.get("started")
        ended = attrs.get("ended")
        if (started and ended) is not None and started > ended:
            errors.setdefault("invalid_dates", []).append(
                "Дата завершения проекта не может быть раньше даты начала."
            )

        if errors:
            raise serializers.ValidationError(errors)
        return attrs


class ProjectOrDraftCreateMixin:
    """Миксин создания проекта или его черновика."""

    def create(self, validated_data) -> Project:
        """Метод создания проекта или его черновика."""

        directions = validated_data.pop("directions", None)
        project_specialists = validated_data.pop("project_specialists", None)
        with transaction.atomic():
            project_instance, _ = Project.objects.get_or_create(
                **validated_data
            )
            if directions is not None:
                project_instance.directions.set(directions)
            if project_specialists is not None:
                for project_specialist_data in project_specialists:
                    skills_data = project_specialist_data.pop("skills")
                    project_specialist_instance = (
                        ProjectSpecialist.objects.create(
                            project=project_instance, **project_specialist_data
                        )
                    )
                    project_specialist_instance.skills.set(skills_data)
        return project_instance

from datetime import date
from queue import Queue
from typing import Any, Dict, List

from django.db import transaction
from rest_framework import serializers

from apps.general.models import Skill
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


class ProjectOrDraftValidateMixin(serializers.ModelSerializer):
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

        if (
            self.context.get("request").method == "POST"
            and Project.objects.filter(
                name=attrs.get("name"),
                creator=self.context.get("request").user,
            ).exists()
        ):
            errors.setdefault("unique", []).append(
                "У вас уже есть проект или его черновик с таким названием."
            )

        project_specialists_data = attrs.get("project_specialists")
        project_specialists_fields = [
            (data["specialist"], data["level"])
            for data in project_specialists_data
        ]
        if len(project_specialists_data) != len(
            set(project_specialists_fields)
        ):
            errors.setdefault("unique_project_specialists", []).append(
                "Дублирование специалистов c их грейдом для проекта не "
                "допустимо."
            )

        started = attrs.get("started")
        ended = attrs.get("ended")
        if (started and ended) is not None and started > ended:
            errors.setdefault("invalid_dates", []).append(
                "Дата завершения проекта не может быть раньше даты начала."
            )

        if errors:
            raise serializers.ValidationError(errors)
        return super().validate(attrs)


class ProjectOrDraftCreateMixin(serializers.ModelSerializer):
    """Миксин создания проекта или его черновика."""

    def create(self, validated_data) -> Project:
        """Метод создания проекта или его черновика."""

        directions = validated_data.pop("directions", None)
        project_specialists = validated_data.pop("project_specialists", None)

        project_specialists_to_create = []
        skills_data_to_create: Queue[List[Skill]] = Queue()

        with transaction.atomic():
            project_instance = super().create(validated_data)

            if directions is not None:
                project_instance.directions.set(directions)

            if project_specialists is not None:
                for project_specialist_data in project_specialists:
                    skills_data_to_create.put(
                        project_specialist_data.pop("skills")
                    )
                    project_specialist_data["project_id"] = project_instance.id
                    project_specialists_to_create.append(
                        ProjectSpecialist(**project_specialist_data)
                    )

                created_project_specialists = (
                    ProjectSpecialist.objects.bulk_create(
                        project_specialists_to_create
                    )
                )
                for project_specialist in created_project_specialists:
                    skills_data = skills_data_to_create.get()
                    project_specialist.skills.set(skills_data)
        return project_instance


class ToRepresentationOnlyIdMixin:
    """Миксин с методом to_representation, возвращающим только id объекта."""

    def to_representation(self, instance):
        """Метод представления объекта в виде словаря с полем 'id'."""

        return {"id": instance.id}

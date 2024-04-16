from datetime import date
from queue import Queue
from typing import Any, Dict, List

from django.db import transaction
from rest_framework import serializers

from apps.general.models import Skill
from apps.projects.models import Project, ProjectSpecialist


class RecruitmentStatusMixin:
    """Миксин определения статуса набора в проект."""

    def get_recruitment_status(self, obj) -> str:
        """Метод определения статуса набора в проект."""

        if any(
            profession.is_required
            for profession in obj.project_specialists.all()
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

    def _check_not_unique_project_name(self, request=None, name=None) -> bool:
        """
        Метод проверки уникальности создаваемого или редактируемого проекта или
        его черновика по названию для создателя.
        """

        if request is not None and request.method in ("PUT", "PATCH", "POST"):
            if name is not None:
                queryset = Project.objects.filter(
                    name=name, creator=request.user
                )
                instance = getattr(self, "instance", None)
                if instance is not None:
                    queryset = queryset.exclude(id=instance.id)
                return queryset.exists()
        return False

    def _check_not_unique_project_specialists(
        self, project_specialists_data=None
    ) -> bool:
        """
        Метод проверки дублирования специалистов необходимых проекту по их
        профессии и грейду.
        """

        if project_specialists_data is not None:
            project_specialists_fields = [
                (data["profession"], data["level"])
                for data in project_specialists_data
            ]
            return len(project_specialists_data) != len(
                set(project_specialists_fields)
            )
        return False

    def validate_started(self, value) -> date:
        """Метод валидации даты начала проекта."""

        return self._validate_date(value, "начала проекта")

    def validate_ended(self, value) -> date:
        """Метод валидации даты завершения проекта."""

        return self._validate_date(value, "завершения проекта")

    def validate(self, attrs) -> Dict[str, Any]:
        """Метод валидации данных проекта или черновика."""

        request = getattr(self, "context").get("request")
        errors: Dict = {}

        if self._check_not_unique_project_name(
            request, name=attrs.get("name", None)
        ):
            errors.setdefault("unique", []).append(
                "У вас уже есть проект или его черновик с таким названием."
            )

        project_specialists_data = attrs.get("project_specialists", None)
        if self._check_not_unique_project_specialists(
            project_specialists_data
        ):
            errors.setdefault("unique_project_specialists", []).append(
                "Дублирование специалистов c их грейдом для проекта не "
                "допустимо."
            )

        recruitment_status = request.data.get("recruitment_status", None)
        if (
            recruitment_status is not None
            and project_specialists_data is not None
        ):
            if not recruitment_status:
                for specialist in project_specialists_data:
                    specialist["is_required"] = False
            elif not any(
                [
                    specialist["is_required"]
                    for specialist in project_specialists_data
                ]
            ):
                errors.setdefault("is_required", []).append(
                    "Отметьте хотя бы одного специалиста для поиска в "
                    "проект."
                )

        started = attrs.get("started", None)
        ended = attrs.get("ended", None)
        if (started and ended) is not None and started > ended:
            errors.setdefault("invalid_dates", []).append(
                "Дата завершения проекта не может быть раньше даты начала."
            )

        if errors:
            raise serializers.ValidationError(errors)
        return attrs


class ProjectOrDraftCreateUpdateMixin:
    """Миксин создания и редактирования проекта или его черновика."""

    def process_project_specialists(
        self, project_instance, project_specialists
    ) -> None:
        """Метод обработки специалистов необходимых проекту."""
        project_specialists_to_update = []
        skills_data_to_process: Queue[List[Skill]] = Queue()

        if project_specialists is not None:
            project_instance.project_specialists.all().delete()

            for project_specialist_data in project_specialists:
                skills_data_to_process.put(
                    project_specialist_data.pop("skills", [])
                )
                project_specialist_data["project_id"] = project_instance.id
                project_specialists_to_update.append(
                    ProjectSpecialist(**project_specialist_data)
                )

            created_project_specialists = (
                ProjectSpecialist.objects.bulk_create(
                    project_specialists_to_update
                )
            )

            for project_specialist in created_project_specialists:
                skills_data = skills_data_to_process.get()
                if skills_data:
                    project_specialist.skills.set(skills_data)

    def create(self, validated_data) -> Project:
        """Метод создания проекта или его черновика."""

        project_specialists = validated_data.pop("project_specialists", None)

        with transaction.atomic():
            project_instance = super().create(validated_data)  # type: ignore
            self.process_project_specialists(
                project_instance, project_specialists
            )

        return project_instance

    def update(self, instance, validated_data) -> Project:
        """Метод обновления проекта или его черновика."""

        _ = validated_data.pop("project_specialists", None)

        with transaction.atomic():
            project_instance = super().update(  # type: ignore
                instance, validated_data
            )

        return project_instance

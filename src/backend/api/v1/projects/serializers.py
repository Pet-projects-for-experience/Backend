from datetime import date
from queue import Queue
from typing import Any, Dict, List, Optional

from django.db import transaction
from rest_framework import serializers

from api.v1.general.serializers import SkillSerializer, SpecialistSerializer
from apps.general.models import Skill
from apps.projects.constants import BUSYNESS_CHOICES, STATUS_CHOICES
from apps.projects.mixins import RecruitmentStatusMixin
from apps.projects.models import Direction, Project, ProjectSpecialist


class DirectionSerializer(serializers.ModelSerializer):
    """Сериализатор направления разработки."""

    class Meta:
        model = Direction
        fields = "__all__"


class ReadProjectSpecialistSerializer(SpecialistSerializer):
    """Сериализатор для чтения специалиста необходимого проекту."""

    specialist = SpecialistSerializer()
    skills = SkillSerializer(many=True)
    level = serializers.SerializerMethodField()

    class Meta:
        model = ProjectSpecialist
        fields = (
            "id",
            "specialist",
            "skills",
            "count",
            "level",
            "is_required",
        )

    def get_level(self, obj) -> str:
        """Метод получения представления для грейда."""

        return obj.get_level_display()


class WriteProjectSpecialistSerializer(SpecialistSerializer):
    """Сериализатор для записи специалиста необходимого проекту."""

    class Meta:
        model = ProjectSpecialist
        fields = (
            "id",
            "specialist",
            "skills",
            "count",
            "level",
            "is_required",
        )


class ReadProjectSerializer(
    RecruitmentStatusMixin, serializers.ModelSerializer
):
    """Сериализатор для чтения проектов."""

    directions = serializers.StringRelatedField(many=True)
    status = serializers.ChoiceField(
        choices=STATUS_CHOICES, source="get_status_display"
    )
    recruitment_status = serializers.SerializerMethodField()
    project_specialists = ReadProjectSpecialistSerializer(many=True)
    creator = serializers.SlugRelatedField(
        slug_field="username", read_only=True
    )
    owner = serializers.SlugRelatedField(slug_field="username", read_only=True)

    class Meta:
        model = Project
        fields = (
            "id",
            "name",
            "description",
            "started",
            "ended",
            "directions",
            "creator",
            "owner",
            "link",
            "recruitment_status",
            "project_specialists",
            "status",
        )
        read_only_fields = fields

    def get_recruitment_status(self, obj) -> str:
        """Метод определения статуса набора в проект."""

        return self.calculate_recruitment_status(obj)


class WriteProjectSerializer(
    RecruitmentStatusMixin, serializers.ModelSerializer
):
    """Сериализатор для записи проектов."""

    creator = serializers.SerializerMethodField(read_only=True)
    owner = serializers.SerializerMethodField(read_only=True)
    project_specialists = WriteProjectSpecialistSerializer(many=True)
    busyness = serializers.ChoiceField(
        choices=BUSYNESS_CHOICES, write_only=True
    )
    project_busyness = serializers.ChoiceField(
        choices=BUSYNESS_CHOICES,
        source="get_busyness_display",
        read_only=True,
    )
    status = serializers.ChoiceField(choices=STATUS_CHOICES, write_only=True)
    project_status = serializers.ChoiceField(
        choices=STATUS_CHOICES,
        source="get_status_display",
        read_only=True,
    )
    recruitment_status = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = (
            "id",
            "name",
            "description",
            "started",
            "ended",
            "busyness",
            "project_busyness",
            "directions",
            "creator",
            "owner",
            "link",
            "recruitment_status",
            "project_specialists",
            "status",
            "project_status",
        )
        extra_kwargs = {
            "description": {"required": True},
            "started": {"required": True},
            "ended": {"required": True},
            "busyness": {"required": True},
            "directions": {"required": True},
            "link": {"required": True},
        }

    def get_creator(self, obj) -> str:
        """Метод получения username у создателя проекта."""

        return obj.creator.username

    def get_owner(self, obj) -> str:
        """Метод получения username у владельца проекта."""

        return obj.owner.username

    def get_recruitment_status(self, obj) -> str:
        """Метод определения статуса набора в проект."""

        return self.calculate_recruitment_status(obj)

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

    def validate_status(self, value) -> int:
        """Метод валидации статуса проекта."""

        if value == Project.DRAFT:
            raise serializers.ValidationError(
                "У проекта не может быть статуса 'Черновик'."
            )
        return value

    def validate(self, attrs) -> Dict[str, Any]:
        """Метод валидации данных о проекте."""

        errors: Dict = {}

        queryset = Project.objects.filter(
            name=attrs.get("name"),
            creator=self.context.get("request").user,
        )

        if queryset.exists():
            errors.setdefault("unique", []).append(
                "У вас уже есть проект или его черновик с таким названием."
            )
        if attrs.get("started") > attrs.get("ended"):
            errors.setdefault("invalid_dates", []).append(
                "Дата завершения проекта не может быть раньше даты начала."
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
                "`допустимо."
            )

        if errors:
            raise serializers.ValidationError(errors)
        return super().validate(attrs)

    def create(self, validated_data) -> Project:
        """Метод создания проекта."""

        directions = validated_data.pop("directions")
        project_specialists = validated_data.pop("project_specialists")

        project_specialists_to_create = []
        skills_data_to_create: Queue[List[Skill]] = Queue()

        with transaction.atomic():
            project_instance = super().create(validated_data)
            project_instance.directions.set(directions)

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


class ProjectPreviewMainSerializer(serializers.ModelSerializer):
    """Сериализатор превью проектов."""

    specialists = serializers.SerializerMethodField()
    directions = serializers.StringRelatedField(many=True)

    def get_specialists(self, obj) -> Optional[List[Dict[str, Any]]]:
        """Метод получения списка специалистов."""

        return [
            SpecialistSerializer(specialist.specialist).data
            for specialist in obj.project_specialists.all()
        ]

    class Meta:
        model = Project
        fields = (
            "id",
            "name",
            "started",
            "ended",
            "directions",
            "specialists",
        )

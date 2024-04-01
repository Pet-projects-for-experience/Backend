from typing import Any, Dict, List, Optional

from rest_framework import serializers

from api.v1.general.serializers import SkillSerializer, SpecialistSerializer
from api.v1.projects.mixins import (
    ProjectOrDraftCreateMixin,
    ProjectOrDraftValidateMixin,
    RecruitmentStatusMixin,
)
from apps.projects.constants import BUSYNESS_CHOICES, STATUS_CHOICES
from apps.projects.models import Direction, Project, ProjectSpecialist


class DirectionSerializer(serializers.ModelSerializer):
    """Сериализатор специалиста."""

    class Meta:
        model = Direction
        fields = "__all__"


class BaseProjectSpecialistSerializer(serializers.ModelSerializer):
    """Общий сериализатор для специалиста необходимого проекту."""

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


class ReadProjectSpecialistSerializer(BaseProjectSpecialistSerializer):
    """Сериализатор для чтения специалиста необходимого проекту."""

    specialist = SpecialistSerializer()
    skills = SkillSerializer(many=True)
    level = serializers.SerializerMethodField()

    def get_level(self, obj) -> str:
        """Метод получения представления для грейда."""

        return obj.get_level_display()


class BaseProjectSerializerMixin(RecruitmentStatusMixin):
    """Общий сериализатор для проектов и черновиков."""

    class Meta:
        model = Project
        fields = (
            "id",
            "name",
            "description",
            "started",
            "ended",
            "busyness",
            "directions",
            "creator",
            "owner",
            "link",
            "recruitment_status",
            "project_specialists",
            "status",
        )

    def _get_base_fields(self):
        return {
            "creator": serializers.SlugRelatedField(
                slug_field="username", read_only=True
            ),
            "owner": serializers.SlugRelatedField(
                slug_field="username", read_only=True
            ),
        }

    def get_fields(self):
        fields = super().get_fields()
        fields.update(self._get_base_fields())
        return fields

    def get_recruitment_status(self, obj) -> str:
        """Метод определения статуса набора в проект."""

        return self.calculate_recruitment_status(obj)


class ReadProjectSerializer(
    BaseProjectSerializerMixin,
    serializers.ModelSerializer,
):
    """Сериализатор для чтения проектов."""

    directions = serializers.StringRelatedField(many=True)
    status = serializers.ChoiceField(
        choices=STATUS_CHOICES, source="get_status_display"
    )
    recruitment_status = serializers.SerializerMethodField()
    project_specialists = ReadProjectSpecialistSerializer(many=True)


class WriteProjectSerializer(
    BaseProjectSerializerMixin,
    ProjectOrDraftValidateMixin,
    ProjectOrDraftCreateMixin,
    serializers.ModelSerializer,
):
    """Сериализатор для записи проектов."""

    project_specialists = BaseProjectSpecialistSerializer(
        many=True,
    )
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

    class Meta(BaseProjectSerializerMixin.Meta):
        fields = BaseProjectSerializerMixin.Meta.fields + (  # type: ignore
            "project_busyness",
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

    def validate_status(self, value) -> int:
        """Метод валидации статуса проекта."""

        if value == Project.DRAFT:
            raise serializers.ValidationError(
                "У проекта не может быть статуса 'Черновик'."
            )
        return value


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


class DraftSerializer(
    BaseProjectSerializerMixin,
    ProjectOrDraftValidateMixin,
    ProjectOrDraftCreateMixin,
    serializers.ModelSerializer,
):
    """Сериализатор черновиков проекта."""

    status = serializers.ChoiceField(choices=STATUS_CHOICES, read_only=True)
    link = serializers.URLField(read_only=True)
    project_specialists = BaseProjectSpecialistSerializer(
        many=True, required=False
    )
    recruitment_status = serializers.SerializerMethodField()

    class Meta(BaseProjectSerializerMixin.Meta):
        pass

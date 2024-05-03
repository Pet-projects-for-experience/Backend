from typing import Any, Dict

from rest_framework import serializers

from api.v1.general.mixins import ToRepresentationOnlyIdMixin
from api.v1.general.serializers import ProfessionSerializer, SkillSerializer
from api.v1.projects.mixins import (
    ProjectOrDraftCreateUpdateMixin,
    ProjectOrDraftValidateMixin,
    RecruitmentStatusMixin,
)
from apps.projects.constants import BUSYNESS_CHOICES, PROJECT_STATUS_CHOICES
from apps.projects.models import Direction, Project, ProjectSpecialist


class DirectionSerializer(serializers.ModelSerializer):
    """Сериализатор направления разработки."""

    class Meta:
        model = Direction
        fields = "__all__"


class BaseProjectSpecialistSerializer(serializers.ModelSerializer):
    """Общий сериализатор для специалиста необходимого проекту."""

    class Meta:
        model = ProjectSpecialist
        fields = (
            "id",
            "profession",
            "skills",
            "count",
            "level",
            "is_required",
        )


class ReadProjectSpecialistSerializer(BaseProjectSpecialistSerializer):
    """Сериализатор для чтения специалиста необходимого проекту."""

    profession = ProfessionSerializer()
    skills = SkillSerializer(many=True)
    level = serializers.SerializerMethodField()

    def get_level(self, obj) -> str:
        """Метод получения представления для грейда."""

        return obj.get_level_display()


class BaseProjectSerializer(serializers.ModelSerializer):
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
            "phone_number",
            "telegram_nick",
            "email",
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


class ReadProjectSerializer(RecruitmentStatusMixin, BaseProjectSerializer):
    """Сериализатор для чтения проектов."""

    directions = DirectionSerializer(many=True)
    status = serializers.ChoiceField(
        choices=PROJECT_STATUS_CHOICES, source="get_status_display"
    )
    busyness = serializers.ChoiceField(
        choices=BUSYNESS_CHOICES, source="get_busyness_display"
    )
    project_specialists = ReadProjectSpecialistSerializer(many=True)
    recruitment_status = serializers.SerializerMethodField()
    is_favorite = serializers.SerializerMethodField(read_only=True)

    class Meta(BaseProjectSerializer.Meta):
        fields = BaseProjectSerializer.Meta.fields + (  # type: ignore
            "recruitment_status",
            "is_favorite",
        )

    def get_is_favorite(self, project) -> bool:
        """
        Метод возвращает True если user добавил проект в избранное.
        В противном случе возвращает False.
        Для неавторизованных пользователей всегда возвращает False.
        """
        user = self.context["request"].user
        if user.is_authenticated:
            return bool(user in project.is_favorite.all())
        return False


class WriteProjectSerializer(
    ToRepresentationOnlyIdMixin,
    ProjectOrDraftValidateMixin,
    ProjectOrDraftCreateUpdateMixin,
    BaseProjectSerializer,
):
    """Сериализатор для записи проектов."""

    project_specialists = BaseProjectSpecialistSerializer(many=True)

    class Meta(BaseProjectSerializer.Meta):
        extra_kwargs = {
            "description": {"required": True},
            "started": {"required": True},
            "ended": {"required": True},
            "busyness": {"required": True},
            "directions": {"required": True},
            "link": {"required": False},
            "status": {"required": False},
        }

    def validate_status(self, value) -> int:
        """Метод валидации статуса проекта."""

        if value == Project.DRAFT:
            raise serializers.ValidationError(
                "У проекта не может быть статуса 'Черновик'."
            )
        return value


class ShortProjectSpecialistSerializer(BaseProjectSpecialistSerializer):
    """Сериализатор специалистов проектов краткий."""

    profession = ProfessionSerializer()

    class Meta(BaseProjectSpecialistSerializer.Meta):
        fields = (  # type: ignore
            "id",
            "profession",
            "is_required",
        )


class ProjectPreviewMainSerializer(serializers.ModelSerializer):
    """Сериализатор превью проектов."""

    project_specialists = ShortProjectSpecialistSerializer(many=True)
    directions = DirectionSerializer(many=True)

    class Meta:
        model = Project
        fields = (
            "id",
            "name",
            "started",
            "ended",
            "directions",
            "project_specialists",
        )


class ReadDraftSerializer(ReadProjectSerializer):
    pass


class WriteDraftSerializer(
    ToRepresentationOnlyIdMixin,
    ProjectOrDraftValidateMixin,
    ProjectOrDraftCreateUpdateMixin,
    BaseProjectSerializer,
):
    """Сериализатор черновиков проекта."""

    project_specialists = BaseProjectSpecialistSerializer(
        many=True, required=False
    )

    class Meta(BaseProjectSerializer.Meta):
        extra_kwargs = {
            "status": {"required": False},
            "directions": {"required": False},
        }


class WriteProjectSpecialistSerializer(
    ToRepresentationOnlyIdMixin,
    BaseProjectSpecialistSerializer,
):
    """Сериализатор для записи специалиста необходимого проекту."""

    def validate(self, attrs) -> Dict[str, Any]:
        """Метод валидации специалиста проекта."""

        errors: Dict = {}

        queryset = ProjectSpecialist.objects.filter(
            project_id=self.instance.project.id,
            profession=(
                attrs.get("profession", None) or self.instance.profession
            ),
            level=(attrs.get("level", None) or self.instance.level),
        ).exclude(id=self.instance.id)
        if queryset.exists():
            errors.setdefault("unique", []).append(
                "У данного проекта уже есть специалист с такой профессией и "
                "грейдом."
            )

        if errors:
            raise serializers.ValidationError(errors)
        return attrs

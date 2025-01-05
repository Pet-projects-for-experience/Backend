import html
from itertools import chain
from typing import Any, ClassVar, Dict, Optional, OrderedDict, Tuple

import bleach
from django.db import transaction
from rest_framework import serializers

from api.v1.general.mixins import ToRepresentationOnlyIdMixin
from api.v1.general.serializers import (
    CustomModelSerializer,
    ProfessionSerializer,
    SkillSerializer,
)
from api.v1.profile.serializers import BaseProfileSerializer
from api.v1.projects.constants import (
    ALLOWED_ATTRIBUTES_BY_FRONT,
    ALLOWED_TAGS_BY_FRONT,
)
from api.v1.projects.mixins import (
    ProjectOrDraftCreateUpdateMixin,
    ProjectOrDraftValidateMixin,
    RecruitmentStatusMixin,
)
from apps.projects.constants import (
    BUSYNESS_CHOICES,
    PROJECT_STATUS_CHOICES,
    RequestStatuses,
)
from apps.projects.models import (
    Direction,
    InvitationToProject,
    ParticipationRequest,
    Project,
    ProjectParticipant,
    ProjectSpecialist,
)


class DirectionSerializer(CustomModelSerializer):
    """Сериализатор направления разработки."""

    class Meta:
        model = Direction
        fields = "__all__"


class BaseProjectSpecialistSerializer(CustomModelSerializer):
    """Общий сериализатор для специалиста необходимого проекту."""

    class Meta:
        model = ProjectSpecialist
        fields: ClassVar[Tuple[str, ...]] = (
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


class BaseProjectSerializer(CustomModelSerializer):
    """Общий сериализатор для проектов и черновиков."""

    class Meta:
        model = Project
        fields: ClassVar[Tuple[str, ...]] = (
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
            "project_status",
        )
        read_only_fields: ClassVar[Tuple[str, ...]] = (
            "creator",
            "owner",
        )


class ReadParticipantSerializer(CustomModelSerializer):
    """Сериализатор на чтение участника проекта."""

    user_id = serializers.IntegerField(source="user.profile.user_id")
    avatar = serializers.ImageField(source="user.profile.avatar")
    profession = ProfessionSerializer()
    visible_status = serializers.IntegerField(
        source="user.profile.visible_status"
    )

    class Meta:
        model = ProjectParticipant
        fields = (
            "user_id",
            "avatar",
            "profession",
            "visible_status",
        )
        read_only_fields = fields


class ReadProjectSerializer(RecruitmentStatusMixin, BaseProjectSerializer):
    """Сериализатор для чтения проекта."""

    directions = DirectionSerializer(many=True)
    project_status = serializers.ChoiceField(
        choices=PROJECT_STATUS_CHOICES, source="get_project_status_display"
    )
    busyness = serializers.ChoiceField(
        choices=BUSYNESS_CHOICES, source="get_busyness_display"
    )
    project_specialists = ReadProjectSpecialistSerializer(many=True)
    recruitment_status = serializers.SerializerMethodField()
    is_favorite = serializers.SerializerMethodField(read_only=True)
    owner = serializers.SerializerMethodField()
    creator = serializers.SlugRelatedField(
        slug_field="username", read_only=True
    )
    project_participants = ReadParticipantSerializer(many=True)
    unique_project_participants_skills = serializers.SerializerMethodField()

    class Meta(BaseProjectSerializer.Meta):
        fields: ClassVar[Tuple[str, ...]] = (
            *BaseProjectSerializer.Meta.fields,
            "recruitment_status",
            "is_favorite",
            "project_participants",
            "unique_project_participants_skills",
        )

    def get_is_favorite(self, project) -> bool:
        """
        Метод возвращает True если user добавил проект в избранное.
        В противном случе возвращает False.
        Для неавторизованных пользователей всегда возвращает False.
        """
        request = self.context.get("request", None)
        if user := getattr(request, "user", None):
            if user.is_authenticated:
                return project.favorited_by.filter(id=user.id).exists()
        return False

    def get_owner(self, project) -> dict[str, Any]:
        """Метод возвращает требуемые поля для владельца."""
        owner = project.owner
        return {
            "id": owner.id,
            "username": owner.username,
            "name": owner.profile.name,
            "avatar": (
                owner.profile.avatar.url if owner.profile.avatar else None
            ),
            "visible_status": owner.profile.visible_status,
        }

    def get_unique_project_participants_skills(self, obj) -> list[Any]:
        all_skills = chain.from_iterable(
            [
                participant.skills.values_list("name", flat=True)
                for participant in ProjectParticipant.objects.filter(
                    project=obj
                )
            ]
        )
        return list(set(all_skills))

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["description"] = html.unescape(rep["description"])
        return rep


class WriteProjectSerializer(
    ToRepresentationOnlyIdMixin,
    ProjectOrDraftValidateMixin,
    ProjectOrDraftCreateUpdateMixin,
    BaseProjectSerializer,
):
    """Сериализатор для записи проекта."""

    project_specialists = BaseProjectSpecialistSerializer(many=True)

    class Meta(BaseProjectSerializer.Meta):
        extra_kwargs = {
            "description": {"required": True},
            "started": {"required": True},
            "ended": {"required": True},
            "busyness": {"required": True},
            "project_status": {"required": False},
        }

    def validate_project_status(self, value) -> int:
        """Метод валидации статуса проекта."""

        if value == Project.DRAFT:
            raise serializers.ValidationError(
                "У проекта не может быть статуса 'Черновик'."
            )
        return value

    def validate_description(self, value):
        """
        Метод валидации и защиты от потенциально вредоносных
        HTML-тегов и атрибутов.
        """

        safe_description = bleach.clean(
            value,
            tags=ALLOWED_TAGS_BY_FRONT,
            attributes=ALLOWED_ATTRIBUTES_BY_FRONT,
        )
        return safe_description


class ShortProjectSpecialistSerializer(BaseProjectSpecialistSerializer):
    """Сериализатор для чтения специалиста необходимого проекту краткий."""

    profession = ProfessionSerializer()

    class Meta(BaseProjectSpecialistSerializer.Meta):
        fields: ClassVar[Tuple[str, ...]] = (
            "profession",
            "is_required",
        )


class ProjectPreviewMainSerializer(CustomModelSerializer):
    """Сериализатор для чтения превью проекта на главной странице."""

    project_specialists = ReadProjectSpecialistSerializer(many=True)
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
    """Сериализатор для чтения черновика проекта."""

    pass


class WriteDraftSerializer(
    ToRepresentationOnlyIdMixin,
    ProjectOrDraftValidateMixin,
    ProjectOrDraftCreateUpdateMixin,
    BaseProjectSerializer,
):
    """Сериализатор для записи черновика проекта."""

    project_specialists = BaseProjectSpecialistSerializer(
        many=True, required=False
    )

    class Meta(BaseProjectSerializer.Meta):
        extra_kwargs = {
            "directions": {"required": False},
            "project_status": {"required": False},
        }


class WriteProjectSpecialistSerializer(
    ToRepresentationOnlyIdMixin,
    BaseProjectSpecialistSerializer,
):
    """Сериализатор для записи специалиста необходимого проекту."""

    def validate(self, attrs) -> Dict[str, Any]:
        """Метод валидации атрибутов специалиста необходимого проекту."""

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


class BaseParticipationRequestSerializer(CustomModelSerializer):
    """Базовый сериализатор запросов на участие в проекте."""

    class Meta:
        model = ParticipationRequest
        fields: ClassVar[Tuple[str, ...]] = (
            "project",
            "position",
        )


class ShortProjectSerializer(CustomModelSerializer):
    """Сериализатор краткой информации на чтение проектов."""

    directions = DirectionSerializer(many=True)
    project_status = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = (
            "name",
            "started",
            "ended",
            "directions",
            "project_status",
        )

    def __init__(self, *args, **kwargs):
        exclude = kwargs.pop("exclude", None)
        super().__init__(*args, **kwargs)
        if exclude:
            for field in exclude:
                self.fields.pop(field, None)

    def get_project_status(self, obj) -> str:
        """Метод получения статуса запроса."""
        return obj.get_project_status_display()


class MyRequestsSerializer(CustomModelSerializer):
    """."""

    project = ShortProjectSerializer(exclude=("project_status"))
    request_status = serializers.SerializerMethodField()
    position = serializers.SerializerMethodField()

    class Meta:
        model = ParticipationRequest
        fields = (
            "id",
            "request_status",
            "position",
            "cover_letter",
            "project",
            "answer",
        )

    def get_position(self, obj) -> str:
        """Метод получения specialization из ProfessionSerializer."""
        return ProfessionSerializer(obj.position.profession).data[
            "specialization"
        ]

    def get_request_status(self, obj) -> str:
        """Метод получения статуса запроса."""
        return obj.get_request_status_display()


class UpdateParticipationRequestSerializer(
    ToRepresentationOnlyIdMixin,
    CustomModelSerializer,
):
    """Сериализатор для обновления сопроводительного письма."""

    class Meta:
        model = ParticipationRequest
        fields: ClassVar[Tuple[str, ...]] = ("cover_letter",)


class WriteParticipationRequestSerializer(
    ToRepresentationOnlyIdMixin,
    BaseParticipationRequestSerializer,
):
    """Сериализатор для записи запроса на участие в проекте."""

    class Meta(BaseParticipationRequestSerializer.Meta):
        fields: ClassVar[Tuple[str, ...]] = (
            *BaseParticipationRequestSerializer.Meta.fields,
            "cover_letter",
        )

    def _get_existing_participation_request(
        self, attrs=None
    ) -> Optional[ParticipationRequest]:
        """
        Метод получения существующего запроса на участие в проекте."""

        if attrs:
            filters: Dict = {
                "user": self.context.get("request").user,
                "request_status": RequestStatuses.IN_PROGRESS,
            }
            filters_keys = ("project", "position")
            for filter_key in filters_keys:
                if filter_value := attrs.get(
                    filter_key,
                    (
                        getattr(self.instance, filter_key)
                        if self.instance
                        else None
                    ),
                ):
                    filters[filter_key] = filter_value
            queryset = ParticipationRequest.objects.filter(**filters)
            if self.instance:
                queryset = queryset.exclude(id=self.instance.id)
            return queryset.first()
        return None

    def validate_project(self, value):
        """
        Метод проверки является ли пользователь автором, владельцем или
        участником проекта.
        """

        user = self.context.get("request").user
        project = (
            Project.objects.filter(id=value.id)
            .select_related(
                "owner",
                "creator",
            )
            .prefetch_related(
                "participants",
            )
            .first()
        )
        if (
            user == project.creator
            or user == project.owner
            or user == project.participants
        ):
            raise serializers.ValidationError(
                "Вы не можете создать заявку на участие в проекте, в котором "
                "уже участвуете."
            )
        return value

    def validate_position(self, value):
        """
        Метод, проверяет, является ли позиция валидной для данного проекта.
        """

        project_id = self.initial_data.get("project")
        if project_id is None:
            raise serializers.ValidationError("Проект не найден.")
        try:
            project = Project.objects.get(pk=project_id)
            print(f"Смотрим заходим ли смы сюда и что тут будет {project}")
        except Project.DoesNotExist:
            raise serializers.ValidationError("Проект не найден.")
        request = self.context.get("request")
        if request.method in ("PATCH", "PUT", "POST"):
            project_specialists = project.project_specialists.filter(
                is_required=True
            )
            required_specializations = {
                specialist for specialist in project_specialists
            }

            print(f"Требуемые специальности: {required_specializations}")
            if value not in required_specializations:
                raise serializers.ValidationError(
                    f"Специальность '{value.profession.specialization}' "
                    f"не требуется в проекте '{project.name}'."
                )
            print(f"Переданное значение: {value}")
            return value
        return value

    def validate(self, attrs) -> Dict[str, Any]:
        """Метод валидации атрибутов запроса на участие в проекте."""
        errors: Dict = {}
        request = self.context.get("request")

        if request.method in ("POST", "PATCH", "PUT"):
            participation_request = self._get_existing_participation_request(
                attrs=attrs
            )
            if participation_request is not None:
                status_errors_types = {
                    RequestStatuses.IN_PROGRESS: ("unique_in_progress"),
                    RequestStatuses.REJECTED: ("unique_rejected"),
                    RequestStatuses.ACCEPTED: ("unique_accepted"),
                }
                error_type = status_errors_types.get(
                    participation_request.request_status, "unknown"
                )
                errors.setdefault(error_type, []).append(
                    f"Заявка на участие в данном проекте на данную позицию у "
                    f"Вас уже существует и находится в статусе "
                    f"'{participation_request.get_request_status_display()}'."
                )
        if errors:
            raise serializers.ValidationError(errors)
        return attrs

    def validate_cover_letter(self, value):
        escaped_html = bleach.clean(
            value,
            tags=ALLOWED_TAGS_BY_FRONT,
            attributes=ALLOWED_ATTRIBUTES_BY_FRONT,
        )  # защита потенциально вредоносных HTML-тегов и атрибутов
        return escaped_html


class ReadListParticipationRequestSerializer(
    BaseParticipationRequestSerializer
):
    """Сериализатор на чтение списка запросов на участие в проекте."""

    project = ShortProjectSerializer(
        exclude=["started", "ended", "direction", "project_status"]
    )
    position = ShortProjectSpecialistSerializer()
    request_status = serializers.SerializerMethodField()
    request_participants = BaseProfileSerializer(
        exclude=[
            "user_id",
            "specialists",
        ],
        source="user.profile",
    )

    class Meta(BaseParticipationRequestSerializer.Meta):
        fields: ClassVar[Tuple[str, ...]] = (
            *BaseParticipationRequestSerializer.Meta.fields,
            "request_participants",
            "request_status",
            "is_viewed",
            "cover_letter",
        )
        read_only_field = ("request_participants",)

        def to_representation(self, instance):
            rep = super().to_representation(instance)
            rep["cover_letter"] = instance.cover_letter
            return rep

    def get_request_status(self, obj) -> str:
        """Метод получения статуса запроса."""

        return obj.get_request_status_display()


# Вообще не нужно нам просматривать детальную заявку, такой страницы нет даже!
# class ReadRetrieveParticipationRequestSerializer(
#     ReadListParticipationRequestSerializer
# ):
#     """Сериализатор на чтение объекта запроса на участие в проекте."""

#     position = ReadProjectSpecialistSerializer()

#     class Meta(ReadListParticipationRequestSerializer.Meta):
#         fields: ClassVar[Tuple[str, ...]] = (
#             *ReadListParticipationRequestSerializer.Meta.fields,
#             "cover_letter",
#             "created",
#         )

#     def to_representation(self, instance):
#         rep = super().to_representation(instance)
#         rep["cover_letter"] = html.unescape(rep["cover_letter"])
#         return rep


class WriteParticipationRequestAnswerSerializer(
    ToRepresentationOnlyIdMixin,
    BaseParticipationRequestSerializer,
):
    """Сериализатор на запись ответа на заявку на участие в проекте."""

    class Meta(BaseParticipationRequestSerializer.Meta):
        fields: ClassVar[Tuple[str, ...]] = (
            "id",
            "answer",
            "request_status",
        )

    def validate_request_status(self, value) -> int:
        """Метод валидации статуса заявки на участие в проекте."""

        if value not in (RequestStatuses.ACCEPTED, RequestStatuses.REJECTED):
            raise serializers.ValidationError(
                "При ответе, заявку можно только принять или отклонить."
            )
        return value

    def validate(self, attrs) -> Dict[str, Any]:
        """Метод валидации атрибутов заявки на участие в проекте."""

        errors: Dict = {}

        if attrs.get("request_status", None) == RequestStatuses.ACCEPTED:
            participants = getattr(self.instance.project, "participants", None)
            user = getattr(self.instance, "user", None)
            if (
                participants
                and user
                and participants.filter(id=user.id).exists()
            ):
                errors.setdefault("already", []).append(
                    "Этот специалист уже участвует в проекте."
                )

        if errors:
            raise serializers.ValidationError(errors)
        return attrs

    def update(self, instance, validated_data) -> ParticipationRequest:
        """Метод обновления заявки на участие в проекте."""

        if (
            validated_data.get("request_status", None)
            == RequestStatuses.ACCEPTED
        ):
            with transaction.atomic():
                project_participant = ProjectParticipant.objects.create(
                    project=instance.project,
                    user=instance.user,
                    profession=instance.position.profession,
                )
                project_participant.skills.set(instance.position.skills.all())
        return super().update(instance, validated_data)


# class ReadInvitationToProjectSerializer(
#     ReadRetrieveParticipationRequestSerializer
# ):
#     """Сериализатор на чтение приглашений в проект."""

#     class Meta(ReadRetrieveParticipationRequestSerializer.Meta):
#         model = InvitationToProject
#         fields: ClassVar[Tuple[str, ...]] = (
#             *ReadRetrieveParticipationRequestSerializer.Meta.fields,
#             "author",
#         )

#     def to_representation(self, instance):
#         rep = super().to_representation(instance)
#         rep["cover_letter"] = html.unescape(rep["cover_letter"])
#         return rep


class WriteInvitationToProjectSerializer(
    ToRepresentationOnlyIdMixin, BaseParticipationRequestSerializer
):
    """Сериализатор на запись приглашения в проект."""

    class Meta:
        model = InvitationToProject
        fields: ClassVar[Tuple[str, ...]] = (
            "position",
            "project",
            "cover_letter",
            "user",
        )

    def validate(self, attrs) -> OrderedDict:
        """Метод валидации атрибутов приглашения."""
        errors: Dict = {}
        project = attrs.get("project", None)
        user = attrs.get("user", None)
        position = attrs.get("position", None)
        if not project.project_specialists.filter(
            id=position.id,
            is_required=True,
        ).exists():
            errors.setdefault("position", []).append(
                "Этот специалист не требуется проекту"
            )
        if (
            project.participants.filter(id=user.id).exists()
            or project.invitation_to_project.filter(user=user).exists()
        ):
            errors.setdefault("user", []).append(
                "Этот пользователь уже участвует в проекте или приглашен"
            )
        if not user.profile.professions.filter(
            speciality=position.profession.speciality,
            specialization=position.profession.specialization,
        ).exists():
            errors.setdefault("user", []).append(
                "У пользователя нет подходящей специальности"
            )
        if errors:
            raise serializers.ValidationError(errors)
        return attrs

    def validate_cover_letter(self, value):
        escaped_html = bleach.clean(
            value,
            tags=ALLOWED_TAGS_BY_FRONT,
            attributes=ALLOWED_ATTRIBUTES_BY_FRONT,
        )  # защита потенциально вредоносных HTML-тегов и атрибутов
        return escaped_html


class PartialWriteInvitationToProjectSerializer(
    CustomModelSerializer, ToRepresentationOnlyIdMixin
):
    """Сериализатор на обновление приглашения в проект."""

    class Meta:
        model = InvitationToProject
        fields: ClassVar[Tuple[str, ...]] = ("request_status", "answer")

    def validate(self, attrs) -> OrderedDict:
        user = self.context["request"].user
        if self.instance.user != user:
            raise serializers.ValidationError(
                {"error": "Вы не можете изменить приглашение"}
            )

        return attrs

    def update(self, instance, validated_data) -> ParticipationRequest:
        """Метод обновления приглашения на участие в проекте.
        Так же добавляет пользователя в участники проекта"""

        if (
            validated_data.get("request_status", None)
            == RequestStatuses.ACCEPTED
        ):
            with transaction.atomic():
                project_participant = ProjectParticipant.objects.create(
                    project=instance.project,
                    user=instance.user,
                    profession=instance.position.profession,
                )
                project_participant.skills.set(instance.position.skills.all())
        return super().update(instance, validated_data)

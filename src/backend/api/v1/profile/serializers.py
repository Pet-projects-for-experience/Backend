import html
from typing import ClassVar, Optional

import bleach
from django.core.validators import RegexValidator
from django.db.models import Q
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator, UniqueValidator

from api.v1.general.fields import Base64ImageField
from api.v1.general.mixins import ToRepresentationOnlyIdMixin
from api.v1.general.serializers import (
    CustomModelSerializer,
    ProfessionSerializer,
    SkillSerializer,
)

# from api.v1.profile.constants import (
#     ALLOWED_ATTRIBUTES_BY_FRONT,
#     ALLOWED_TAGS_BY_FRONT,
# )
from apps.general.constants import MAX_SKILLS, MAX_SKILLS_MESSAGE
from apps.general.models import Profession
from apps.profile.constants import MAX_SPECIALISTS, MAX_SPECIALISTS_MESSAGE
from apps.profile.models import Profile, Specialist
from apps.projects.models import Project
from apps.users.constants import (
    MAX_LENGTH_USERNAME,
    MIN_LENGTH_USERNAME,
    USERNAME_ERROR_REGEX_TEXT,
    USERNAME_REGEX,
)


class CurrentProfile(serializers.CurrentUserDefault):
    """Получение профиля текущего пользователя."""

    def __call__(self, serializer_field):
        return serializer_field.context["request"].user.profile


class BaseSpecialistSerializer(CustomModelSerializer):
    """Базовый сериализатор специалиста."""

    class Meta:
        model = Specialist
        fields: ClassVar[tuple[str, ...]] = (
            "id",
            "profession",
            "level",
            "skills",
        )


class SpecialistReadSerializer(BaseSpecialistSerializer):
    """Сериализатор для чтения специализаций в профиле."""

    profession = ProfessionSerializer(read_only=True)
    skills = SkillSerializer(many=True, read_only=True)

    class Meta(BaseSpecialistSerializer.Meta):
        read_only_fields = BaseSpecialistSerializer.Meta.fields


class SpecialistWriteSerializer(
    ToRepresentationOnlyIdMixin, BaseSpecialistSerializer
):
    """Сериализатор для создания, редактирования специализаций в профиле."""

    profession = serializers.PrimaryKeyRelatedField(
        queryset=Profession.objects.all()
    )
    profile = serializers.HiddenField(default=CurrentProfile())

    class Meta(BaseSpecialistSerializer.Meta):
        fields: ClassVar[tuple[str, ...]] = (
            *SpecialistReadSerializer.Meta.fields,
            "profile",
        )
        validators = (
            UniqueTogetherValidator(
                queryset=(Specialist.objects.all()),
                fields=("profession", "profile"),
            ),
        )

    @staticmethod
    def check_duplicates(values) -> str | bool:
        duplicates = {value.id for value in values if values.count(value) > 1}
        if duplicates:
            return f"Значения дублируются: {duplicates}"
        return False

    def validate_profile(self, profile):
        if profile.specialists.count() >= MAX_SPECIALISTS:
            raise serializers.ValidationError(MAX_SPECIALISTS_MESSAGE)
        return profile

    def validate_skills(self, skills) -> list[int]:
        errors = list()
        if duplicates := self.check_duplicates(skills):
            errors.append(duplicates)
        if len(skills) > MAX_SKILLS:
            errors.append(MAX_SKILLS_MESSAGE)
        if errors:
            raise serializers.ValidationError(errors)
        return skills

    def create(self, validated_data):
        skills = validated_data.pop("skills")
        specialist = super().create(validated_data)
        specialist.skills.set(skills)
        return specialist

    def update(self, specialist, validated_data):
        if "skills" in validated_data:
            specialist.skills.set(validated_data.pop("skills"))
        return super().update(specialist, validated_data)


class BaseProfileSerializer(CustomModelSerializer):
    """Базовый класс для сериализаторов профилей."""

    username = serializers.CharField(source="user.username", read_only=True)
    specialists = SpecialistReadSerializer(many=True, read_only=True)

    class Meta:
        model = Profile
        fields: ClassVar[tuple[str, ...]] = (
            "user_id",
            "avatar",
            "username",
            "name",
            "ready_to_participate",
            "specialists",
        )

    def __init__(self, *args, **kwargs):
        exclude = kwargs.pop("exclude", None)
        super().__init__(*args, **kwargs)
        if exclude:
            for field in exclude:
                self.fields.pop(field, None)


class ProfilePreviewReadSerializer(BaseProfileSerializer):
    """Сериализатор для чтения превью профилей специалистов."""

    is_favorite = serializers.SerializerMethodField(read_only=True)

    class Meta(BaseProfileSerializer.Meta):
        fields: ClassVar[tuple[str, ...]] = (
            *BaseProfileSerializer.Meta.fields,
            "is_favorite",
        )
        read_only_fields = fields

    def get_is_favorite(self, profile) -> bool:
        user = self.context["request"].user
        return (
            user.is_authenticated
            and profile.favorited_by.filter(id=user.pk).exists()
        )


class ProfileDetailReadSerializer(ProfilePreviewReadSerializer):
    """Сериализатор для чтения подробной информации профиля специалиста."""

    projects = serializers.SerializerMethodField(read_only=True)

    class Meta(ProfilePreviewReadSerializer.Meta):
        fields: ClassVar[tuple[str, ...]] = (
            *ProfilePreviewReadSerializer.Meta.fields,
            "about",
            "portfolio_link",
            "birthday",
            "country",
            "city",
            "phone_number",
            "telegram_nick",
            "email",
            "projects",
        )

    @staticmethod
    def get_projects(profile: Profile) -> list[Optional[dict]]:
        """
        Получение активных и завершенных проектов специалиста,
        где он участник, организатор и/или владелец.
        """

        user = profile.user
        user_projects = (
            Project.objects.filter(
                Q(creator=user) | Q(participants=user) | Q(owner=user)
            )
            .exclude(project_status=Project.DRAFT)
            .only("id", "name")
        )

        return [
            dict(id=project.pk, name=project.name) for project in user_projects
        ]

    def to_representation(self, profile):
        """Представление контактов согласно настройкам видимости."""

        data = super().to_representation(profile)
        user = self.context["request"].user
        visibility = profile.visible_status_contacts
        if visibility == Profile.VisibilitySettings.NOBODY or (
            not (user.is_authenticated and user.is_organizer)
            and visibility == Profile.VisibilitySettings.CREATOR_ONLY
        ):
            for contact_field in ["phone_number", "telegram_nick", "email"]:
                data[contact_field] = None
        data["about"] = html.unescape(data["about"]) if data["about"] else ""
        return data


class ProfileMeReadSerializer(BaseProfileSerializer):
    """Сериализатор для чтения профиля его владельцем."""

    class Meta(BaseProfileSerializer.Meta):
        fields: ClassVar[tuple[str, ...]] = (
            *BaseProfileSerializer.Meta.fields,
            "about",
            "portfolio_link",
            "phone_number",
            "telegram_nick",
            "email",
            "birthday",
            "country",
            "city",
            "visible_status",
            "visible_status_contacts",
            "allow_notifications",
            "subscribe_to_projects",
        )
        read_only_fields = fields

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["about"] = html.unescape(rep["about"]) if rep["about"] else ""
        return rep


class ProfileMeWriteSerializer(ProfileMeReadSerializer):
    """Сериализатор для обновления профиля его владельцем."""

    avatar = Base64ImageField(required=False, allow_null=True)
    username = serializers.CharField(
        source="user__username",
        required=False,
        min_length=MIN_LENGTH_USERNAME,
        max_length=MAX_LENGTH_USERNAME,
        validators=(
            RegexValidator(
                regex=USERNAME_REGEX, message=USERNAME_ERROR_REGEX_TEXT
            ),
            UniqueValidator(queryset=Profile.objects.all()),
        ),
    )

    class Meta(ProfileMeReadSerializer.Meta):
        read_only_fields = ("user_id", "specialists")

    def validate_about(self, value):
        """
        Метод валидации и защиты от потенциально вредоносных
        HTML-тегов и атрибутов.
        """

        safe_about = bleach.clean(value)
        return safe_about

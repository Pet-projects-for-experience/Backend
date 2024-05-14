from typing import ClassVar, Optional

from django.core.validators import RegexValidator
from django.db.models import Q
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from api.v1.general.fields import Base64ImageField, SkillField
from api.v1.general.mixins import ToRepresentationOnlyIdMixin
from api.v1.general.serializers import ProfessionSerializer, SkillSerializer
from apps.general.models import Profession, Skill
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


class SpecialistReadSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения специализаций в профиле."""

    profession = ProfessionSerializer(read_only=True)
    skills = SkillSerializer(many=True, read_only=True)

    class Meta:
        model = Specialist
        fields = ("id", "profession", "level", "skills")
        read_only_fields = fields


class SpecialistWriteSerializer(
    ToRepresentationOnlyIdMixin, SpecialistReadSerializer
):
    """Сериализатор для создания, редактирования специализаций в профиле."""

    profession = serializers.PrimaryKeyRelatedField(
        queryset=Profession.objects.all()
    )
    skills = SkillField(many=True, queryset=Skill.objects.all())
    profile = serializers.HiddenField(default=CurrentProfile())

    class Meta:
        model = Specialist
        fields = (*SpecialistReadSerializer.Meta.fields, "profile")
        validators = (
            UniqueTogetherValidator(
                queryset=(Specialist.objects.all()),
                fields=("profession", "profile"),
            ),
        )

    @staticmethod
    def check_empty(value):
        if not value:
            raise serializers.ValidationError("Пустое значение.")
        return value

    @staticmethod
    def check_duplicates(values):
        duplicates = {value.id for value in values if values.count(value) > 1}
        if duplicates:
            raise serializers.ValidationError(
                f"Значения дублируются: {duplicates}"
            )
        return values

    def validate_profile(self, profile):
        if profile.specialists.count() >= MAX_SPECIALISTS:
            raise serializers.ValidationError(MAX_SPECIALISTS_MESSAGE)
        return profile

    def validate_skills(self, skills):
        self.check_empty(skills)
        self.check_duplicates(skills)
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


class ProfilePreviewReadSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения превью профилей специалистов."""

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
        read_only_fields = fields


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
            .exclude(status=Project.DRAFT)
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
        return data


class ProfileMeReadSerializer(ProfilePreviewReadSerializer):
    """Сериализатор для чтения профиля его владельцем."""

    class Meta(ProfilePreviewReadSerializer.Meta):
        fields: ClassVar[tuple[str, ...]] = (
            *ProfilePreviewReadSerializer.Meta.fields,
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
        ),
    )

    class Meta(ProfileMeReadSerializer.Meta):
        pass

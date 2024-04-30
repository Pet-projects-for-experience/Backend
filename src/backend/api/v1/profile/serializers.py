from base64 import b64decode

from django.core.files.base import ContentFile
from django.core.validators import RegexValidator
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from api.v1.general.mixins import ToRepresentationOnlyIdMixin
from api.v1.general.serializers import ProfessionSerializer, SkillSerializer
from apps.general.models import Profession, Skill
from apps.profile.models import Profile, Specialist
from apps.users.constants import (
    MAX_LENGTH_USERNAME,
    MIN_LENGTH_USERNAME,
    USERNAME_ERROR_REGEX_TEXT,
    USERNAME_REGEX,
)


class SkillField(serializers.PrimaryKeyRelatedField):
    """
    Поле навыков: запись по первичному ключу,
    чтение в виде вложенной структуры.
    """

    def to_representation(self, skill):
        return SkillSerializer(skill).data


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


class ProfileReadSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения профиля его владельцем."""

    username = serializers.CharField(source="user.username", read_only=True)
    specialists = SpecialistReadSerializer(many=True, read_only=True)

    class Meta:
        model = Profile
        fields = (
            "user_id",
            "avatar",
            "username",
            "name",
            "about",
            "portfolio_link",
            "phone_number",
            "telegram_nick",
            "email",
            "birthday",
            "country",
            "city",
            "specialists",
            "ready_to_participate",
            "visible_status",
            "visible_status_contacts",
            "allow_notifications",
            "subscribe_to_projects",
        )
        read_only_fields = fields


class Base64ImageField(serializers.ImageField):
    """Обработка изображений в формате base64."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith("data:image"):
            format, imgstr = data.split(";base64,")
            extension = format.split("/")[-1]
            data = ContentFile(b64decode(imgstr), name="temp." + extension)
        return super().to_internal_value(data)


class ProfileWriteSerializer(ProfileReadSerializer):
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

    class Meta:
        model = Profile
        fields = ProfileReadSerializer.Meta.fields
        read_only_fields = ("user_id",)

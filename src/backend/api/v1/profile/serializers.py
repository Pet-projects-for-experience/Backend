from base64 import b64decode

from django.core.files.base import ContentFile
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from api.v1.general.serializers import ProfessionSerializer, SkillSerializer
from apps.general.models import Profession, Skill
from apps.profile.models import Profile, Specialist


class SkillField(serializers.PrimaryKeyRelatedField):

    def to_representation(self, skill):
        return SkillSerializer(skill).data


class ProfileProfessionReadSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения специализаций в профиле."""
    profession = ProfessionSerializer(read_only=True)
    specialist_id = serializers.IntegerField(source="id", read_only=True)
    skills = SkillField(many=True, read_only=True)

    class Meta:
        model = Specialist
        fields = (
            "specialist_id",
            "profession",
            "level",
            "skills"
        )
        read_only_fields = fields


class CurrentProfile(serializers.CurrentUserDefault):

    def __call__(self, serializer_field):
        return serializer_field.context['request'].user.profile


class ProfileProfessionWriteSerializer(ProfileProfessionReadSerializer):
    """Сериализатор для создания, редактирования специализаций в профиле."""
    profession = serializers.PrimaryKeyRelatedField(
        queryset=Profession.objects.all()
    )
    skills = SkillField(many=True, queryset=Skill.objects.all())
    profile = serializers.HiddenField(default=CurrentProfile())

    class Meta:
        model = Specialist
        fields = (*ProfileProfessionReadSerializer.Meta.fields, "profile")
        validators = (
            UniqueTogetherValidator(
                queryset=(
                    Specialist.objects.select_related("profession")
                    .prefetch_related("skills").all()
                ),
                fields=("profession", "profile")
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


class ProfileReadSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения профиля его владельцем."""

    username = serializers.CharField(source="user.username", read_only=True)
    professions = ProfileProfessionReadSerializer(
        source="specialists", many=True, read_only=True
    )

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
            "professions",
            "ready_to_participate",
            "visible_status",
            "visible_status_contacts",
            "allow_notifications",
            "subscribe_to_projects"
        )
        read_only_fields = fields


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith("data:image"):
            format, imgstr = data.split(";base64,")
            extension = format.split("/")[-1]
            data = ContentFile(b64decode(imgstr), name="temp." + extension)
        return super().to_internal_value(data)


class ProfileWriteSerializer(ProfileReadSerializer):
    """Сериализатор для обновления профиля его владельцем."""
    avatar = Base64ImageField(required=False, allow_null=True)
    username = serializers.CharField(source="user__username")

    class Meta(ProfileReadSerializer.Meta):
        read_only_fields = ("user_id",)

    def to_representation(self, instance):
        return ProfileReadSerializer(instance).data

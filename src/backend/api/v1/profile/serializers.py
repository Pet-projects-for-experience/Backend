from rest_framework import serializers

from apps.profile.models import Profile, Specialist
from apps.profile.constants import MAX_PROFILE_PROFESSIONS
from apps.general.models import Profession


def validate_empty(value):
    if not value:
        raise serializers.ValidationError("Пустое значение.")
    return value


def validate_duplicates(values):
    duplicates = {value.id for value in values if values.count(value) > 1}
    if duplicates:
        raise serializers.ValidationError(
            f"Значения дублируются: {duplicates}"
        )
    return values


def validate_length(values, max_length):
    if len(values) > max_length:
        raise serializers.ValidationError(
            f"Можно добавить не более {max_length}."
        )
    return values


class SpecialistSerializer(serializers.ModelSerializer):
    profession_id = serializers.PrimaryKeyRelatedField(
        source="profession",
        queryset=Profession.objects.all()
    )
    specialty = serializers.CharField(
        source="profession.specialty",
        read_only=True
    )
    specialization = serializers.CharField(
        source="profession.specialization",
        read_only=True
    )

    class Meta:
        model = Specialist
        fields = (
            "profession_id",
            "specialty",
            "specialization",
            "level",
            "skills",
        )

    def validate_skills(self, skills):
        validate_empty(skills)
        validate_duplicates(skills)
        return skills


class SettingProfileSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения, обновления профиля его владельцем."""
    username = serializers.CharField(source="user.username", read_only=True)
    professions = SpecialistSerializer(source="profile_professions", many=True)

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
            "visible_status_contacts"
        )
        read_only_fields = ("user_id",)

    def validate_professions(self, professions):
        validate_empty(professions)
        validate_length(professions, MAX_PROFILE_PROFESSIONS)
        validate_duplicates([
            specialist["profession"] for specialist in professions
        ])
        return professions

    def update(self, profile, validated_data):
        if "profile_professions" in validated_data:
            professions_data = validated_data.pop("profile_professions")
            profile.professions.clear()
            for profile_profession in professions_data:
                specialist = Specialist.objects.create(
                    profile=profile,
                    profession=profile_profession["profession"],
                    level=profile_profession.get("level")
                )
                if "skills" in profile_profession:
                    specialist.skills.set(profile_profession.pop("skills"))
        return super().update(profile, validated_data)

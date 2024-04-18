from rest_framework import serializers

from apps.profile.models import Profile, UserSkill, UserSpecialization
from apps.projects.models import Profession, Skill


class ProfileSerializer(serializers.ModelSerializer):
    """Сериализатор на просмотр профиля с учетом выбора видимости контактов."""

    class Meta:
        model = Profile
        # fields = "__all__"
        exclude = ["visible_status_contacts", "visible_status", "user"]

    def to_representation(self, instance):
        user = self.context["request"].user
        visible_status_contacts = instance.visible_status_contacts
        is_organizer = user.is_authenticated and user.is_organizer
        base_queryset = super().to_representation(instance)
        if visible_status_contacts in [Profile.NOBODY] or (
            not is_organizer
            and visible_status_contacts in [Profile.CREATOR_ONLY]
        ):
            base_queryset.pop("phone_number")
            base_queryset.pop("email")
            base_queryset.pop("telegram_nick")
        return base_queryset


class UserSkillSerializer(serializers.ModelSerializer):
    skill = serializers.PrimaryKeyRelatedField(
        queryset=Skill.objects.all(), many=True
    )

    class Meta:
        model = UserSkill
        fields = ["user", "skill"]
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=UserSkill.objects.all(),
                fields=["user", "skill"],
                message="Этот навык вами уже был выбран",
            )
        ]


class UserSpecializationSerializer(serializers.ModelSerializer):
    specialization = serializers.PrimaryKeyRelatedField(
        queryset=Profession.objects.all(), many=True
    )

    class Meta:
        model = UserSpecialization
        fields = ["user", "specialization"]
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=UserSpecialization.objects.all(),
                fields=["user", "specialization"],
                message="Этот специализация вами уже была выбрана",
            )
        ]


class ProfileUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор на редактирование профиля пользователя."""

    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    userskills = UserSkillSerializer(many=True, read_only=True)
    userspecialization = UserSpecializationSerializer(
        many=True, read_only=True
    )

    class Meta:
        model = Profile
        exclude = ["visible_status_contacts", "visible_status"]


class ProfileVisibilitySerializer(serializers.ModelSerializer):
    """Сериализатор на управление видимостью профиля"""

    class Meta:
        model = Profile
        fields = ["visible_status_contacts", "visible_status"]

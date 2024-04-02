from rest_framework import serializers

from apps.profile.models import Profile, UserSkill, UserSpecialization
from apps.projects.models import Skill, Specialist


class ProfileSerializer(serializers.Serializer):
    """Сериализатор на просмотр профиля с учетом выбора видимости контактов."""

    class Meta:
        model = Profile
        fields = "__all__"

    def to_representation(self, instance):
        user = self.context["request"].user
        visible_status_contacts = instance.visible_status_contacts
        if visible_status_contacts in [Profile.NOBODY] or (
            not user.is_organizer
            and visible_status_contacts in [Profile.CREATOR_ONLY]
        ):
            self.fields.pop("phone_number")
            self.fields.pop("email")
            self.fields.pop("telegram")

        return super().to_representation(instance)


class ProfileUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор на редактирование профиля пользователя."""

    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Profile
        fields = "__all__"


class UserSkillSerializer(serializers.ModelSerializer):
    skills = serializers.PrimaryKeyRelatedField(
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
        queryset=Specialist.objects.all(), many=True
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

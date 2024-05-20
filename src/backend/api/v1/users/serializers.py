from django.contrib.auth import get_user_model
from djoser.serializers import (
    UserCreatePasswordRetypeSerializer,
    UserSerializer,
)

from api.v1.general.mixins import OverridedFieldMappingMixin
from api.v1.users import constants

User = get_user_model()


class CustomUserSerializer(UserSerializer):
    """Сериализатор пользователя."""

    class Meta(UserSerializer.Meta):
        fields = constants.ORDERED_USERS_FIELDS


class CustomUserCreateSerializer(
    OverridedFieldMappingMixin,
    UserCreatePasswordRetypeSerializer,
):
    """Сериализатор для регистрации пользователя с подтверждением пароля."""

    class Meta(UserCreatePasswordRetypeSerializer.Meta):
        fields = constants.ORDERED_USERS_FIELDS + ("password",)

from base64 import b64decode

from django.core.files.base import ContentFile
from rest_framework.serializers import ImageField, PrimaryKeyRelatedField

from .serializers import SkillSerializer


class SkillField(PrimaryKeyRelatedField):
    """
    Поле навыков: запись по первичному ключу,
    чтение в виде вложенной структуры.
    """

    def to_representation(self, skill):
        return SkillSerializer(skill).data


class Base64ImageField(ImageField):
    """Обработка изображений в формате base64."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith("data:image"):
            format, imgstr = data.split(";base64,")
            extension = format.split("/")[-1]
            data = ContentFile(b64decode(imgstr), name="temp." + extension)
        return super().to_internal_value(data)

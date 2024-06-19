from base64 import b64decode

from django.core.files.base import ContentFile
from django.utils.translation import gettext_lazy as _
from rest_framework.fields import CharField
from rest_framework.serializers import ImageField


class Base64ImageField(ImageField):
    """Обработка изображений в формате base64."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith("data:image"):
            format, imgstr = data.split(";base64,")
            extension = format.split("/")[-1]
            data = ContentFile(b64decode(imgstr), name="temp." + extension)
        return super().to_internal_value(data)


class CustomEmailField(CharField):
    """Кастомное поле для email."""

    default_error_messages = {"invalid": _("Enter a valid email address.")}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class CustomURLField(CharField):
    """Кастомное поле для URL."""

    default_error_messages = {"invalid": _("Enter a valid URL.")}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

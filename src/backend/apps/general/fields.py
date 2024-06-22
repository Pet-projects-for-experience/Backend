import re

from django import forms
from django.core.validators import MinLengthValidator, RegexValidator
from django.db.models import CharField, TextField
from django.utils.translation import gettext_lazy as _

from .constants import (
    LENGTH_BASE_TEXT_FIELD_ERROR_TEXT,
    LENGTH_EMAIL_ERROR_TEXT,
    MAX_LENGTH_BASE_TEXT_FIELD,
    MAX_LENGTH_EMAIL,
    MAX_LENGTH_URL,
    MIN_LENGTH_BASE_TEXT_FIELD,
    MIN_LENGTH_EMAIL,
    REGEX_BASE_TEXT_FIELD,
    REGEX_BASE_TEXT_FIELD_ERROR_TEXT,
)
from .validators import CustomEmailValidator, CustomURLValidator


class BaseTextField(TextField):
    """Базовый класс для текстового поля."""

    def __init__(self, *args, **kwargs) -> None:
        if kwargs.get("validators") is None:
            kwargs["validators"] = [
                RegexValidator(
                    regex=REGEX_BASE_TEXT_FIELD,
                    message=REGEX_BASE_TEXT_FIELD_ERROR_TEXT,
                    flags=re.IGNORECASE,
                ),
                MinLengthValidator(
                    limit_value=MIN_LENGTH_BASE_TEXT_FIELD,
                    message=LENGTH_BASE_TEXT_FIELD_ERROR_TEXT,
                ),
            ]
        if kwargs.get("max_length") is None:
            kwargs["max_length"] = MAX_LENGTH_BASE_TEXT_FIELD
        super().__init__(*args, **kwargs)


class CustomEmailField(CharField):
    """Кастомное поле для email."""

    default_validators = [
        MinLengthValidator(
            limit_value=MIN_LENGTH_EMAIL, message=LENGTH_EMAIL_ERROR_TEXT
        ),
        CustomEmailValidator(),
    ]
    description = _("Email address")

    def __init__(self, *args, **kwargs) -> None:
        """Метод инициализации объекта класса."""

        kwargs.setdefault("max_length", MAX_LENGTH_EMAIL)
        kwargs.setdefault("verbose_name", self.description)
        super().__init__(*args, **kwargs)

    def formfield(self, **kwargs) -> forms.EmailField:
        """Метод определения поля формы для данного поля."""

        defaults = {
            "form_class": forms.EmailField,
            "validators": self.default_validators,
        }
        defaults.update(kwargs)
        return super().formfield(**defaults)


class CustomURLField(CharField):
    default_validators = [CustomURLValidator()]
    description = _("URL")

    def __init__(self, *args, **kwargs) -> None:
        """Метод инициализации объекта класса."""

        kwargs.setdefault("max_length", MAX_LENGTH_URL)
        super().__init__(*args, **kwargs)

    def formfield(self, **kwargs) -> forms.URLField:
        """Метод определения поля формы для данного поля."""

        defaults = {
            "form_class": forms.URLField,
            "validators": self.default_validators,
        }
        defaults.update(kwargs)
        return super().formfield(**defaults)

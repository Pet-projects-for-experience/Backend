import re

from django import forms
from django.core.validators import MinLengthValidator, RegexValidator
from django.db.models import EmailField, TextField
from django.utils.translation import gettext_lazy as _

from apps.general.constants import (
    LENGTH_BASE_TEXT_FIELD_ERROR_TEXT,
    LENGTH_EMAIL_ERROR_TEXT,
    MAX_LENGTH_BASE_TEXT_FIELD,
    MAX_LENGTH_EMAIL,
    MIN_LENGTH_BASE_TEXT_FIELD,
    MIN_LENGTH_EMAIL,
    REGEX_BASE_TEXT_FIELD,
    REGEX_BASE_TEXT_FIELD_ERROR_TEXT,
)
from apps.general.validators import CustomEmailValidator


class BaseTextField(TextField):
    """Базовый класс для текстового поля."""

    def __init__(self, *args, **kwargs):
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


class CustomEmailField(EmailField):
    """Кастомное поле для email."""

    default_validators = [
        MinLengthValidator(
            limit_value=MIN_LENGTH_EMAIL, message=LENGTH_EMAIL_ERROR_TEXT
        ),
        CustomEmailValidator(),
    ]
    default_max_length = MAX_LENGTH_EMAIL
    default_verbose_name = _("Email address")

    def __init__(
        self,
        *args,
        verbose_name=None,
        max_length=None,
        **kwargs,
    ) -> None:
        """Метод инициализации объекта класса."""

        self.max_length = max_length or self.default_max_length
        self.verbose_name = verbose_name or self.default_verbose_name
        super().__init__(
            max_length=self.max_length,
            verbose_name=self.verbose_name,
            *args,
            **kwargs,
        )

    def formfield(self, **kwargs) -> forms.EmailField:
        """Метод формирования поля для формы."""

        defaults = {
            "form_class": forms.EmailField,
            "validators": self.default_validators,
        }
        defaults.update(kwargs)
        return super().formfield(**defaults)

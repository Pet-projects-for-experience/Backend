import re

from django.core.validators import MinLengthValidator, RegexValidator
from django.db.models import TextField

from apps.general.constants import (
    LENGTH_BASE_TEXT_FIELD_ERROR_TEXT,
    MAX_LENGTH_BASE_TEXT_FIELD,
    MIN_LENGTH_BASE_TEXT_FIELD,
    REGEX_BASE_TEXT_FIELD,
    REGEX_BASE_TEXT_FIELD_ERROR_TEXT,
)


class BaseTextField(TextField):
    """
    Базовый класс для текстовых полей.
    """

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

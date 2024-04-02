from typing import Any

from django.core.exceptions import ValidationError
from django.utils.functional import SimpleLazyObject
from django.utils.regex_helper import _lazy_re_compile
from django.utils.translation import gettext_lazy as _


class PasswordBaseInit:
    """Базовый класс для валидаторов пароля."""

    message = _("Enter a valid value.")
    code = "password_incorrect"
    help_message = "Проверьте правильность ввода пароля."

    def __init__(self, message=None, code=None, help_message=None) -> None:
        if code is not None:
            self.code = code
        if message is not None:
            self.message = message
        if help_message is not None:
            self.help_message = help_message

    def get_help_text(self) -> str:
        """Получение описательного текста для поля формы."""
        return self.help_message


class PasswordMaximumLengthValidator(PasswordBaseInit):
    """Валидатор максимальной длинны пароля."""

    max_length = 20
    help_message = f"Максимальная длинна: {max_length} символов."

    def __init__(
        self, message=None, code=None, help_message=None, max_length=None
    ) -> None:
        super().__init__(message, code, help_message)
        if max_length is not None:
            self.max_length = max_length

    def validate(self, password, user=None) -> None:
        """Проверка на максимальную длинну пароля."""

        if len(password) > self.max_length:
            raise ValidationError(
                f"{self.message} {self.help_message}",
                code=self.code,
                params={"password": self.help_message},
            )


class PasswordRegexValidator(PasswordBaseInit):
    """Валидатор соответствия вводимого пароля регулярному выражению."""

    regex: Any = ""
    flags = 0

    def __init__(
        self,
        message=None,
        code=None,
        help_message=None,
        regex=None,
        flags=None,
    ) -> None:
        super().__init__(message, code, help_message)
        if regex is not None:
            self.regex = regex
        if flags is not None:
            self.flags = flags
        if self.flags and not isinstance(self.regex, str):
            raise TypeError(
                "Если параметр flags задан, то необходимо задать параметр "
                "regex в виде строки регулярного выражения."
            )
        self.regex: SimpleLazyObject = _lazy_re_compile(self.regex, self.flags)

    def validate(self, password, user=None) -> None:
        """Проверка на соответствие пароля регулярному выражению."""

        if not self.regex.match(password):
            raise ValidationError(
                f"{self.message} {self.help_message}",
                code=self.code,
                params={"password": self.help_message},
            )

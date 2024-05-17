from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from django.utils.deconstruct import deconstructible
from django.utils.regex_helper import _lazy_re_compile


@deconstructible
class CustomEmailValidator(EmailValidator):
    """Кастомный валидатор email адреса."""

    custom_user_regex = _lazy_re_compile(
        r"^[a-z0-9]([^\\x00-\\x7F\\-]?[\w\.-]{0,61}[a-z0-9])?$"
    )
    custom_domain_regex = _lazy_re_compile(
        r"^(?:[a-z0-9]|[a-z0-9][a-z0-9\-]{0,61}[a-z0-9])"
        r"(\.[a-z0-9]|[a-z0-9][a-z0-9\-]{0,61}[a-z0-9])*"
        r"(\.[a-z]{2,})?$"
    )

    def __call__(self, value) -> None:
        """Метод обработки вызова класса как функции."""

        super().__call__(value)
        if not self.custom_validate_email(value):
            raise ValidationError(
                self.message, code=self.code, params={"value": value}
            )

    def __eq__(self, value: object) -> bool:
        """Метод сравнения с другим объектом."""

        return isinstance(value, CustomEmailValidator)

    def custom_validate_user(self, user) -> bool:
        """Кастомный метод валидации пользовательской части email."""

        return bool(self.custom_user_regex.match(user))

    def custom_validate_domain(self, domain) -> bool:
        """Кастомный метод валидации доменной части email."""

        return bool(self.custom_domain_regex.match(domain))

    def custom_validate_email(self, email) -> bool:
        """Кастомный метод валидации email."""

        user, domain = email.split("@")
        return self.custom_validate_user(user) and self.custom_validate_domain(
            domain
        )

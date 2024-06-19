import re
from urllib.parse import urlsplit, urlunsplit

from django.core.exceptions import ValidationError
from django.core.validators import (
    EmailValidator,
    RegexValidator,
    validate_ipv6_address,
)
from django.utils.deconstruct import deconstructible
from django.utils.encoding import punycode
from django.utils.regex_helper import _lazy_re_compile
from django.utils.translation import gettext_lazy as _


@deconstructible
class CustomEmailValidator(EmailValidator):
    """Кастомный валидатор email адреса."""

    custom_user_regex = _lazy_re_compile(
        r"^[a-z0-9]([^\\x00-\\x7F\\-]?[\w\.-]{0,61}[a-z0-9])?$",
        re.IGNORECASE,
    )
    custom_domain_regex = _lazy_re_compile(
        r"^(?:[a-z0-9]|[a-z0-9][a-z0-9\-]{0,61}[a-z0-9])"
        r"(\.[a-z0-9]|[a-z0-9][a-z0-9\-]{0,61}[a-z0-9])*"
        r"(\.[a-z]{2,})?$",
        re.IGNORECASE,
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


@deconstructible
class CustomURLValidator(RegexValidator):
    """Кастомный валидатор URL-адреса."""

    ul = "\u0410-\u044F"
    ui = "\u007f-\u0400\u0402-\u040f\u0450-\u0450\u0452-\ud7ff"

    ipv4_re = (
        r"(?:0|25[0-5]|2[0-4][0-9]|1[0-9]?[0-9]?|[1-9][0-9]?)"
        r"(?:\.(?:0|25[0-5]|2[0-4][0-9]|1[0-9]?[0-9]?|[1-9][0-9]?)){3}"
    )
    ipv6_re = r"\[[0-9a-f:.]+\]"

    hostname_re = (
        r"[a-z"
        + ul
        + r"0-9](?:[a-z"
        + ul
        + r"0-9-]{0,61}[a-z"
        + ul
        + r"0-9])?"
    )

    domain_re = r"(?:\.(?!-)[a-z" + ul + r"0-9-]{1,63}(?<!-))*"
    tld_re = (
        r"\."
        r"(?!-)"
        r"(?:[a-z" + ul + "-]{2,63}"
        r"|xn--[a-z0-9]{1,59})"
        r"(?<!-)"
        r"\.?"
    )
    host_re = "(" + hostname_re + domain_re + tld_re + "|localhost)"

    regex = _lazy_re_compile(
        r"^(?:[a-z0-9.+-]*)://"
        r"(?:[^\s:@/]+(?::[^\s:@/]*)?@)?"
        r"(?:" + ipv4_re + "|" + ipv6_re + "|" + host_re + ")"
        r"(?::[0-9]{1,5})?"
        r"(?:[/?#][^\s]*)?"
        r"\Z",
        re.IGNORECASE,
    )
    message = _("Enter a valid URL.")
    schemes = ["http", "https", "ftp", "ftps"]
    unsafe_chars = frozenset("\t\r\n")
    max_length = 2048

    def __init__(self, schemes=None, **kwargs):
        """Метод инициализации объекта класса."""

        super().__init__(**kwargs)
        if schemes is not None:
            self.schemes = schemes

    def _pre_check_value(self, value) -> None:
        """Метод предварительно проверки валидности value."""

        if (
            not isinstance(value, str)
            or len(value) > self.max_length
            or self.unsafe_chars.intersection(value)
        ):
            raise ValidationError(
                self.message, code=self.code, params={"value": value}
            )

    def _pre_check_scheme(self, value) -> None:
        """Метод предварительно проверки схемы."""

        scheme = value.split("://")[0].lower()
        if not scheme or scheme not in self.schemes:
            raise ValidationError(
                self.message, code=self.code, params={"value": value}
            )

    def _splitted_value(self, value) -> list[str]:
        """Метод разделения value на составляющие."""

        try:
            splitted_url = urlsplit(value)
        except ValueError:
            raise ValidationError(
                self.message, code=self.code, params={"value": value}
            )
        return splitted_url

    def _check_query(self, query) -> None:
        """Метод проверки query."""

        if re.search(f"[{self.ui}]", query):
            raise ValidationError(
                self.message, code=self.code, params={"value": query}
            )

    def __call__(self, value):
        """Метод обработки вызова класса как функции."""

        self._pre_check_value(value)
        self._pre_check_scheme(value)
        splitted_url = self._splitted_value(value)
        self._check_query(splitted_url.query)
        try:
            super().__call__(value)
        except ValidationError as e:
            scheme, netloc, path, query, fragment = splitted_url
            if re.match(r"{self.host_re}\Z", netloc):
                try:
                    netloc = punycode(netloc)
                except UnicodeError:
                    raise e
                url = urlunsplit((scheme, netloc, path, query, fragment))
                super().__call__(url)
            else:
                raise e
        else:
            host_match = re.search(
                r"^\[(.+)\](?::[0-9]{1,5})?$", splitted_url.netloc
            )
            if host_match:
                potential_ip = host_match[1]
                try:
                    validate_ipv6_address(potential_ip)
                except ValidationError:
                    raise ValidationError(
                        self.message, code=self.code, params={"value": value}
                    )

        if splitted_url.hostname is None or len(splitted_url.hostname) > 253:
            raise ValidationError(
                self.message, code=self.code, params={"value": value}
            )

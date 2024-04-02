from django.contrib.auth.models import AbstractUser, UserManager
from django.core.validators import MinLengthValidator, RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.general.constants import MAX_LENGTH_EMAIL
from apps.general.models import CreatedModifiedFields
from apps.users.constants import (
    MAX_LENGTH_USERNAME,
    MIN_LENGTH_USERNAME,
    USERNAME_ERROR_REGEX_TEXT,
    USERNAME_ERROR_TEXT,
    USERNAME_HELP_TEXT,
    USERNAME_REGEX,
)


class CustomUserManager(UserManager):
    """Менеджер объектов пользователей."""

    @classmethod
    def normalize_email(cls, email) -> str:
        """Нормализация email. Приведение символов к нижнему регистру."""

        try:
            email_name, domain_part = email.strip().rsplit("@", 1)
        except ValueError:
            pass
        else:
            email = f"{email_name.lower()}@{domain_part.lower()}"
        return email


class User(CreatedModifiedFields, AbstractUser):
    """Модель пользователя."""

    date_joined = first_name = last_name = None
    email = models.EmailField(
        max_length=MAX_LENGTH_EMAIL,
        unique=True,
        blank=False,
    )
    is_organizer = models.BooleanField(
        verbose_name="Организатор проекта", default=False
    )
    username = models.CharField(
        _("username"),
        max_length=MAX_LENGTH_USERNAME,
        unique=True,
        help_text=USERNAME_HELP_TEXT,
        error_messages={
            "unique": USERNAME_ERROR_TEXT,
        },
        validators=[
            MinLengthValidator(limit_value=MIN_LENGTH_USERNAME),
            RegexValidator(
                regex=USERNAME_REGEX, message=USERNAME_ERROR_REGEX_TEXT
            ),
        ],
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = [
        "username",
    ]

    objects = CustomUserManager()

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
        ordering = (
            "created",
            "username",
        )

    def get_full_name(self) -> str:
        """Метод получения полного имени пользователя."""

        return self.username

    def get_short_name(self) -> str:
        """Метод получения сокращенного имени пользователя."""

        return self.username

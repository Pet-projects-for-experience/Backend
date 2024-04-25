from django.core.validators import MinLengthValidator, RegexValidator
from django.db import models

from apps.general.constants import (
    LENGTH_SPECIALIZATION_NAME_ERROR_TEXT,
    LENGTH_SPECIALTY_NAME_ERROR_TEXT,
    LENGTH_TELEGRAM_NICK_ERROR_TEXT,
    MAX_LENGTH_DESCRIPTION,
    MAX_LENGTH_EMAIL,
    MAX_LENGTH_PHONE_NUMBER,
    MAX_LENGTH_SKILL_NAME,
    MAX_LENGTH_SPECIALIZATION_NAME,
    MAX_LENGTH_SPECIALTY_NAME,
    MAX_LENGTH_TELEGRAM_NICK,
    MAX_LENGTH_TITLE,
    MIN_LENGTH_SPECIALIZATION_NAME,
    MIN_LENGTH_SPECIALTY_NAME,
    MIN_LENGTH_TELEGRAM_NICK,
    REGEX_PHONE_NUMBER,
    REGEX_PHONE_NUMBER_ERROR_TEXT,
    REGEX_SPECIALIZATION_NAME,
    REGEX_SPECIALIZATION_NAME_ERROR_TEXT,
    REGEX_SPECIALTY_NAME,
    REGEX_SPECIALTY_NAME_ERROR_TEXT,
    REGEX_TELEGRAM_NICK,
    REGEX_TELEGRAM_NICK_ERROR_TEXT,
)


class CreatedModifiedFields(models.Model):
    """
    Абстрактная модель. Поля времени создания и последней модификации объекта.
    """

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Section(models.Model):
    """Модель секций страниц."""

    title = models.TextField(
        verbose_name="Заголовок",
        max_length=MAX_LENGTH_TITLE,
        null=False,
    )
    description = models.TextField(
        verbose_name="Текст", max_length=MAX_LENGTH_DESCRIPTION, null=False
    )
    page_id = models.PositiveSmallIntegerField(
        verbose_name="Идентификатор страницы", null=False
    )

    class Meta:
        verbose_name = "Секция"
        verbose_name_plural = "Секции"
        constraints = (
            models.constraints.UniqueConstraint(
                fields=("title", "page_id"),
                name=("%(app_label)s_%(class)s_unique_section_per_page"),
            ),
        )

    def __str__(self):
        """Метод строкового представления объекта секции страницы."""

        return self.title


class Skill(models.Model):
    """Модель навыков."""

    name = models.CharField(
        verbose_name="Название",
        max_length=MAX_LENGTH_SKILL_NAME,
        unique=True,
    )

    class Meta:
        verbose_name = "Навык"
        verbose_name_plural = "Навыки"

    def __str__(self) -> str:
        """Метод строкового представления объекта навыка."""

        return self.name


class Profession(models.Model):
    """Модель профессии."""

    specialty = models.CharField(
        verbose_name="Специализация",
        max_length=MAX_LENGTH_SPECIALTY_NAME,
        validators=(
            MinLengthValidator(
                limit_value=MIN_LENGTH_SPECIALTY_NAME,
                message=LENGTH_SPECIALTY_NAME_ERROR_TEXT,
            ),
            RegexValidator(
                regex=REGEX_SPECIALTY_NAME,
                message=REGEX_SPECIALTY_NAME_ERROR_TEXT,
            ),
        ),
    )
    specialization = models.CharField(
        verbose_name="Специальность",
        max_length=MAX_LENGTH_SPECIALIZATION_NAME,
        validators=(
            MinLengthValidator(
                limit_value=MIN_LENGTH_SPECIALIZATION_NAME,
                message=LENGTH_SPECIALIZATION_NAME_ERROR_TEXT,
            ),
            RegexValidator(
                regex=REGEX_SPECIALIZATION_NAME,
                message=REGEX_SPECIALIZATION_NAME_ERROR_TEXT,
            ),
        ),
    )

    class Meta:
        verbose_name = "Профессия"
        verbose_name_plural = "Профессии"
        constraints = (
            models.constraints.UniqueConstraint(
                fields=("specialty", "specialization"),
                name=("%(app_label)s_%(class)s_unique_profession"),
            ),
        )

    def __str__(self) -> str:
        """Метод строкового представления объекта профессии."""

        return f"{self.specialty} - {self.specialization}"


class ContactsFields(models.Model):
    """Абстрактная модель с полями контактов."""

    phone_number = models.TextField(
        max_length=MAX_LENGTH_PHONE_NUMBER,
        verbose_name="Номер телефона",
        null=True,
        blank=True,
        validators=[
            RegexValidator(
                regex=REGEX_PHONE_NUMBER,
                message=REGEX_PHONE_NUMBER_ERROR_TEXT,
            )
        ],
    )
    telegram_nick = models.CharField(
        max_length=MAX_LENGTH_TELEGRAM_NICK,
        verbose_name="Ник в телеграм",
        null=True,
        blank=True,
        validators=[
            MinLengthValidator(
                limit_value=MIN_LENGTH_TELEGRAM_NICK,
                message=LENGTH_TELEGRAM_NICK_ERROR_TEXT,
            ),
            RegexValidator(
                regex=REGEX_TELEGRAM_NICK,
                message=REGEX_TELEGRAM_NICK_ERROR_TEXT,
            ),
        ],
    )
    email = models.EmailField(
        verbose_name="E-mail",
        max_length=MAX_LENGTH_EMAIL,
        null=True,
        blank=True,
    )

    class Meta:
        abstract = True

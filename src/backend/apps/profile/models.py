from django.core.validators import (
    MinLengthValidator,
    RegexValidator,
    URLValidator,
)
from django.db import models

from apps.general.constants import LEVEL_CHOICES
from apps.general.models import ContactsFields, Profession, Skill
from apps.profile.constants import (
    MAX_LENGTH_ABOUT,
    MAX_LENGTH_CITY,
    MAX_LENGTH_COUNTRY,
    MAX_LENGTH_NAME,
    MAX_LENGTH_URL,
    MAX_LENGTH_URL_MESSAGE,
    MIN_LENGTH_ABOUT,
    MIN_LENGTH_NAME,
    MIN_LENGTH_NAME_MESSAGE,
    MIN_LENGTH_PORTFOLIO,
    REGEX_PROFILE_ABOUT,
    REGEX_PROFILE_ABOUT_MESSAGE,
    REGEX_PROFILE_NAME,
    REGEX_PROFILE_NAME_MESSAGE,
)
from apps.profile.validators import BirthdayValidator, validate_image
from apps.users.models import User


class Profile(ContactsFields, models.Model):
    """Модель профиля пользователя."""

    class VisibilitySettings(models.IntegerChoices):
        ALL = 1, "All"
        CREATOR_ONLY = 2, "Only creator"
        NOBODY = 3, "Nobody"

    user = models.OneToOneField(
        to=User,
        on_delete=models.CASCADE,
        primary_key=True,
        verbose_name="Пользователь",
    )
    avatar = models.ImageField(
        verbose_name="Аватар",
        upload_to="images/",
        validators=[validate_image],
        blank=True,
        null=True
    )
    name = models.CharField(
        verbose_name="Имя",
        max_length=MAX_LENGTH_NAME,
        validators=[
            RegexValidator(
                regex=REGEX_PROFILE_NAME,
                message=REGEX_PROFILE_NAME_MESSAGE,
            ),
            MinLengthValidator(
                limit_value=MIN_LENGTH_NAME,
                message=MIN_LENGTH_NAME_MESSAGE,
            ),
        ],
        blank=False,
    )
    about = models.TextField(
        verbose_name="О себе",
        blank=True,
        max_length=MAX_LENGTH_ABOUT,
        validators=[
            RegexValidator(
                regex=REGEX_PROFILE_ABOUT,
                message=REGEX_PROFILE_ABOUT_MESSAGE,
            ),
            MinLengthValidator(limit_value=MIN_LENGTH_ABOUT),
        ],
    )
    portfolio_link = models.URLField(
        verbose_name="Ссылка на портфолио",
        blank=True,
        max_length=MAX_LENGTH_URL,
        validators=[
            URLValidator(message=MAX_LENGTH_URL_MESSAGE),
            MinLengthValidator(limit_value=MIN_LENGTH_PORTFOLIO),
        ],
    )
    birthday = models.DateField(
        verbose_name="Дата рождения",
        validators=[BirthdayValidator],
        null=True,
        blank=True,
    )
    country = models.CharField(
        verbose_name="Страна",
        max_length=MAX_LENGTH_COUNTRY,
        blank=True
    )
    city = models.CharField(
        verbose_name="Город",
        max_length=MAX_LENGTH_CITY,
        blank=True
    )
    ready_to_participate = models.BooleanField(
        verbose_name="Готов(а) к участию в проектах",
        default=False,
    )
    visible_status = models.PositiveSmallIntegerField(
        verbose_name="Видимость",
        choices=VisibilitySettings.choices,
        default=VisibilitySettings.ALL
    )
    visible_status_contacts = models.PositiveSmallIntegerField(
        verbose_name="Видимость контактов",
        choices=VisibilitySettings.choices,
        default=VisibilitySettings.ALL,
    )
    professions = models.ManyToManyField(
        to=Profession,
        through="Specialist",
        verbose_name="Профессии"
    )
    allow_notifications = models.BooleanField(
        verbose_name="Отправлять уведомления",
        default=True
    )
    subscribe_to_projects = models.BooleanField(
        verbose_name="Подписаться на проекты",
        default=True
    )

    class Meta:
        verbose_name = "Профиль"
        verbose_name_plural = "Профили"

    def __str__(self):
        return f"Профиль {self.pk}"


class Specialist(models.Model):
    """Модель специалиста."""

    profession = models.ForeignKey(
        to=Profession,
        on_delete=models.CASCADE,
        verbose_name="Профессия"
    )
    profile = models.ForeignKey(
        to=Profile,
        on_delete=models.CASCADE,
        verbose_name="Профиль пользователя"
    )
    level = models.IntegerField(
        verbose_name="Уровень квалификации",
        choices=LEVEL_CHOICES,
        null=True,
        blank=True
    )
    skills = models.ManyToManyField(
        to=Skill,
        verbose_name="Навыки"
    )

    class Meta:
        verbose_name = "Специалист"
        verbose_name_plural = "Специалисты"
        constraints = (
            models.UniqueConstraint(
                fields=("profile", "profession"),
                name=(
                    "%(app_label)s_%(class)s_unique_profession_per_profile"
                ),
            ),
        )
        default_related_name = "specialists"

    def __str__(self):
        return f"{self.profile} - {self.profession}"

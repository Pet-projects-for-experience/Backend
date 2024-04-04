from django.core.validators import (
    MinLengthValidator,
    RegexValidator,
    URLValidator,
)
from django.db import models

from apps.general.constants import LEVEL_CHOICES
from apps.general.models import ContactsFields, Skill, Specialist
from apps.profile.constants import (
    BOOL_CHOICES,
    MAX_LENGTH_ABOUT,
    MAX_LENGTH_CITY,
    MAX_LENGTH_COUNTRY,
    MAX_LENGTH_NAME,
    MAX_LENGTH_URL,
    MIN_LENGTH_ABOUT,
    MIN_LENGTH_NAME,
    MIN_LENGTH_PORTFOLIO,
    VISIBLE_CHOICES,
)
from apps.profile.validators import BirthdayValidator, validate_image
from apps.users.models import User


class Profile(ContactsFields, models.Model):
    """Модель профиля пользователя"""

    ALL = 1
    CREATOR_ONLY = 2
    NOBODY = 3

    avatar = models.ImageField(
        verbose_name="Аватар",
        upload_to="images/",
        validators=[validate_image],
    )
    name = models.CharField(
        verbose_name="Имя",
        max_length=MAX_LENGTH_NAME,
        validators=[
            RegexValidator(
                regex=r"^[a-zA-Zа-яА-Я -]+$",
                message="Введите кириллицу или латиницу",
            ),
            MinLengthValidator(
                limit_value=MIN_LENGTH_NAME,
                message="Должно быть минимум символов",
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
                regex=r"^[a-zA-Zа-яА-Я0-9\s!@#$%^&*()-_+=<>?]+$",
                message="Введите кириллицу или латиницу",
            ),
            MinLengthValidator(limit_value=MIN_LENGTH_ABOUT),
        ],
    )
    portfolio_link = models.URLField(
        blank=True,
        max_length=MAX_LENGTH_URL,
        validators=[
            URLValidator(message="Введите корректный URL"),
            MinLengthValidator(limit_value=MIN_LENGTH_PORTFOLIO),
        ],
    )

    birthday = models.DateField(
        verbose_name="Дата рождения", validators=[BirthdayValidator], null=True
    )
    country = models.CharField(
        verbose_name="Страна", max_length=MAX_LENGTH_COUNTRY
    )
    city = models.CharField(verbose_name="Город", max_length=MAX_LENGTH_CITY)
    level = models.IntegerField(
        verbose_name="Уровень квалификации", choices=LEVEL_CHOICES, null=True
    )
    ready_to_participate = models.BooleanField(
        verbose_name="Готовность к участию в проектах",
        choices=BOOL_CHOICES,
        null=True,
    )  # готовность к участию в проектах по умолчанию отключена
    user = models.OneToOneField(
        User, verbose_name="Пользователь", on_delete=models.CASCADE
    )
    visible_status = models.PositiveSmallIntegerField(
        verbose_name="Видимость", choices=VISIBLE_CHOICES, default=ALL
    )
    visible_status_contacts = models.PositiveSmallIntegerField(
        verbose_name="Видимость контактов",
        choices=VISIBLE_CHOICES,
        default=ALL,
    )


class UserSkill(models.Model):
    """Модель навыка пользователя"""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True)

    class Meta:
        verbose_name = "Навык пользователя"
        constraints = (
            models.UniqueConstraint(
                fields=("user", "skill"),
                name=("%(app_label)s_%(class)s_unique_skill_per_user"),
            ),
        )
        default_related_name = "userskills"


class UserSpecialization(models.Model):
    """Модель специализации пользователя"""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    specialization = models.ForeignKey(Specialist, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True)

    class Meta:
        verbose_name = "Специализация пользователя"
        constraints = (
            models.UniqueConstraint(
                fields=("user", "specialization"),
                name=(
                    "%(app_label)s_%(class)s_unique_specialization_per_user"
                ),
            ),
        )
        default_related_name = "userspecialization"

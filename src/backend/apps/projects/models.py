import re

from django.contrib.auth import get_user_model
from django.contrib.postgres.indexes import GinIndex
from django.core.validators import MinLengthValidator, RegexValidator
from django.db import models

from apps.general.constants import LEVEL_CHOICES
from apps.general.fields import BaseTextField, CustomURLField
from apps.general.models import (
    ContactsFields,
    CreatedModifiedFields,
    Profession,
    Skill,
)
from apps.projects.constants import (
    BUSYNESS_CHOICES,
    LENGTH_DESCRIPTION_ERROR_TEXT,
    LENGTH_DIRECTION_NAME_ERROR_TEXT,
    LENGTH_LINK_ERROR_TEXT,
    LENGTH_PROJECT_NAME_ERROR_TEXT,
    MAX_LENGTH_DESCRIPTION,
    MAX_LENGTH_DIRECTION_NAME,
    MAX_LENGTH_LINK,
    MAX_LENGTH_PROJECT_NAME,
    MIN_LENGTH_DESCRIPTION,
    MIN_LENGTH_DIRECTION_NAME,
    MIN_LENGTH_LINK,
    MIN_LENGTH_PROJECT_NAME,
    PROJECT_STATUS_CHOICES,
    REGEX_DESCRIPTION,
    REGEX_DESCRIPTION_NAME_ERROR_TEXT,
    REGEX_DIRECTION_NAME,
    REGEX_DIRECTION_NAME_ERROR_TEXT,
    REGEX_PROJECT_NAME,
    REGEX_PROJECT_NAME_ERROR_TEXT,
    RequestStatuses,
)

User = get_user_model()


class Direction(models.Model):
    """Модель направления разработки."""

    name = models.CharField(
        verbose_name="Название",
        max_length=MAX_LENGTH_DIRECTION_NAME,
        unique=True,
        validators=(
            MinLengthValidator(
                limit_value=MIN_LENGTH_DIRECTION_NAME,
                message=LENGTH_DIRECTION_NAME_ERROR_TEXT,
            ),
            RegexValidator(
                regex=REGEX_DIRECTION_NAME,
                message=REGEX_DIRECTION_NAME_ERROR_TEXT,
            ),
        ),
    )

    class Meta:
        verbose_name = "Направление разработки"
        verbose_name_plural = "Направления разработки"

    def __str__(self) -> str:
        """Метод строкового представления объекта направления разработки."""

        return self.name


class Project(CreatedModifiedFields, ContactsFields):
    """Модель проекта."""

    DRAFT = 1
    ACTIVE = 2
    ENDED = 3

    name = models.CharField(
        verbose_name="Название",
        max_length=MAX_LENGTH_PROJECT_NAME,
        validators=(
            MinLengthValidator(
                limit_value=MIN_LENGTH_PROJECT_NAME,
                message=LENGTH_PROJECT_NAME_ERROR_TEXT,
            ),
            RegexValidator(
                regex=REGEX_PROJECT_NAME,
                message=REGEX_PROJECT_NAME_ERROR_TEXT,
            ),
        ),
    )
    description = models.TextField(
        verbose_name="Описание",
        max_length=MAX_LENGTH_DESCRIPTION,
        null=True,
        validators=(
            MinLengthValidator(
                limit_value=MIN_LENGTH_DESCRIPTION,
                message=LENGTH_DESCRIPTION_ERROR_TEXT,
            ),
            RegexValidator(
                regex=REGEX_DESCRIPTION,
                message=REGEX_DESCRIPTION_NAME_ERROR_TEXT,
                flags=re.IGNORECASE,
            ),
        ),
    )
    creator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="created_projects",
        verbose_name="Организатор",
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="owned_projects",
        verbose_name="Владелец",
    )
    started = models.DateField(
        verbose_name="Дата начала",
        null=True,
    )
    ended = models.DateField(
        verbose_name="Дата завершения",
        null=True,
    )
    busyness = models.PositiveSmallIntegerField(
        verbose_name="Занятость (час/нед)",
        choices=BUSYNESS_CHOICES,
        null=True,
    )
    status = models.PositiveSmallIntegerField(
        verbose_name="Статус",
        choices=PROJECT_STATUS_CHOICES,
    )
    directions = models.ManyToManyField(
        Direction,
        verbose_name="Направления разработки",
        related_name="projects_direction",
    )
    link = CustomURLField(
        verbose_name="Ссылка",
        max_length=MAX_LENGTH_LINK,
        null=True,
        blank=True,
        validators=(
            MinLengthValidator(
                limit_value=MIN_LENGTH_LINK,
                message=LENGTH_LINK_ERROR_TEXT,
            ),
        ),
    )
    participants = models.ManyToManyField(
        User,
        through="ProjectParticipant",
        verbose_name="Участники",
        related_name="projects_participated",
    )

    favorited_by = models.ManyToManyField(
        User,
        verbose_name="Добавили в избранное",
        related_name="favorite_projects",
        blank=True,
    )

    class Meta:
        verbose_name = "Проект"
        verbose_name_plural = "Проекты"
        ordering = ("-created",)
        constraints = (
            models.UniqueConstraint(
                fields=("creator", "name"),
                name=("%(app_label)s_%(class)s_unique_name_per_creator"),
            ),
        )
        indexes = [
            GinIndex(
                fields=["name", "description"],
                name="project_search_idx",
                opclasses=["gin_trgm_ops", "gin_trgm_ops"],
            ),
        ]

    def __str__(self) -> str:
        """Метод строкового представления объекта проекта."""

        return self.name


class ProjectSpecialist(models.Model):
    """Модель специалиста необходимого проекту."""

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        verbose_name="Проект",
    )
    profession = models.ForeignKey(
        Profession,
        on_delete=models.CASCADE,
        verbose_name="профессия",
    )
    skills = models.ManyToManyField(
        Skill,
        verbose_name="Навыки",
    )
    count = models.PositiveSmallIntegerField(
        verbose_name="Количество",
    )
    level = models.PositiveSmallIntegerField(
        verbose_name="Уровень",
        choices=LEVEL_CHOICES,
    )
    is_required = models.BooleanField(
        verbose_name="Требуется",
    )

    class Meta:
        verbose_name = "Специалист проекта"
        verbose_name_plural = "Специалисты проекта"
        default_related_name = "project_specialists"
        constraints = (
            models.UniqueConstraint(
                fields=("project", "profession", "level"),
                name="%(app_label)s_%(class)s_unique_specialist_per_project",
            ),
        )


class ParticipationRequestAndInvitationBasemodel(CreatedModifiedFields):
    """Абстрактная модель для запросов на участие и приглашений в проект."""

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        verbose_name="Проект",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Претендент",
    )
    position = models.ForeignKey(
        ProjectSpecialist,
        on_delete=models.CASCADE,
        verbose_name="Должность",
    )
    status = models.PositiveSmallIntegerField(
        verbose_name="Статус",
        choices=RequestStatuses.choices,
        default=RequestStatuses.IN_PROGRESS,
    )
    is_viewed = models.BooleanField(
        verbose_name="Просмотрено",
        default=False,
    )
    cover_letter = BaseTextField(
        verbose_name="Сопроводительное письмо",
        null=True,
    )
    answer = BaseTextField(
        verbose_name="Ответ",
        null=True,
    )

    class Meta:
        abstract = True


class ParticipationRequest(ParticipationRequestAndInvitationBasemodel):
    """Модель запроса на участие в проекте."""

    class Meta:
        verbose_name = "Запрос на участие"
        verbose_name_plural = "Запросы на участие"
        default_related_name = "participation_requests"
        constraints = (
            models.UniqueConstraint(
                fields=("project", "user", "position"),
                name="%(app_label)s_%(class)s_unique_request_per_project",
                condition=models.Q(status=RequestStatuses.IN_PROGRESS),
            ),
        )

    def __str__(self) -> str:
        """Метод строкового представления объекта запроса на участие."""

        return f"{self.user} - {self.project}"


class InvitationToProject(ParticipationRequestAndInvitationBasemodel):
    """Модель приглашения специалиста в проект"""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Автор",
        related_name="my_invitation_to_project",
    )

    class Meta:
        verbose_name = "Приглашение для участия"
        verbose_name_plural = "Приглашения для участия"
        default_related_name = "invitation_to_project"
        constraints = (
            models.UniqueConstraint(
                fields=("user", "position"),
                name="%(app_label)s_%(class)s_unique_request_per_project",
                condition=models.Q(status=RequestStatuses.IN_PROGRESS),
            ),
        )


class ProjectParticipant(CreatedModifiedFields):
    """Модель участника проекта."""

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        verbose_name="Проект",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Участник",
    )
    profession = models.ForeignKey(
        Profession,
        on_delete=models.CASCADE,
        verbose_name="Профессия",
    )
    skills = models.ManyToManyField(
        Skill,
        verbose_name="Навыки",
    )

    class Meta:
        verbose_name = "Участник проекта"
        verbose_name_plural = "Участники проекта"
        default_related_name = "project_participants"
        constraints = (
            models.UniqueConstraint(
                fields=("project", "user", "profession"),
                name="%(app_label)s_%(class)s_unique_participant_role_per_"
                "project",
            ),
        )

    def __str__(self) -> str:
        """Метод строкового представления объекта участника проекта."""

        return f"{self.user} - {self.project}"

# Generated by Django 5.0.1 on 2024-05-24 10:05

import apps.general.fields
import django.core.validators
import django.db.models.deletion
import re
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("projects", "0010_alter_project_email_alter_project_phone_number"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="InvitationToProject",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("modified", models.DateTimeField(auto_now=True)),
                (
                    "status",
                    models.PositiveSmallIntegerField(
                        choices=[
                            (1, "В процессе"),
                            (2, "Принята"),
                            (3, "Отклонена"),
                        ],
                        default=1,
                        verbose_name="Статус",
                    ),
                ),
                (
                    "is_viewed",
                    models.BooleanField(
                        default=False, verbose_name="Просмотрено"
                    ),
                ),
                (
                    "cover_letter",
                    apps.general.fields.BaseTextField(
                        max_length=750,
                        null=True,
                        validators=[
                            django.core.validators.RegexValidator(
                                flags=re.RegexFlag["IGNORECASE"],
                                message="Поле может содержать: кириллические и латинские символы, цифры и спецсимовлы -!#$%%&'*+/=?^_;():@,.<>`{}~«»",
                                regex="(^[-%!#$&*'+/=?^_;():@,.<>`{|}~-«»0-9A-ZА-ЯЁ\\s]+)\\Z",
                            ),
                            django.core.validators.MinLengthValidator(
                                limit_value=5,
                                message="Длина поля от 5 до 750 символов.",
                            ),
                        ],
                        verbose_name="Сопроводительное письмо",
                    ),
                ),
                (
                    "answer",
                    apps.general.fields.BaseTextField(
                        max_length=750,
                        null=True,
                        validators=[
                            django.core.validators.RegexValidator(
                                flags=re.RegexFlag["IGNORECASE"],
                                message="Поле может содержать: кириллические и латинские символы, цифры и спецсимовлы -!#$%%&'*+/=?^_;():@,.<>`{}~«»",
                                regex="(^[-%!#$&*'+/=?^_;():@,.<>`{|}~-«»0-9A-ZА-ЯЁ\\s]+)\\Z",
                            ),
                            django.core.validators.MinLengthValidator(
                                limit_value=5,
                                message="Длина поля от 5 до 750 символов.",
                            ),
                        ],
                        verbose_name="Ответ",
                    ),
                ),
                (
                    "author",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="my_invitation_to_project",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Автор",
                    ),
                ),
                (
                    "position",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="projects.projectspecialist",
                        verbose_name="Должность",
                    ),
                ),
                (
                    "project",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="projects.project",
                        verbose_name="Проект",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Претендент",
                    ),
                ),
            ],
            options={
                "verbose_name": "Приглашение участника",
                "verbose_name_plural": "Приглашения участников",
                "default_related_name": "invitation_to_project",
            },
        ),
        migrations.AddConstraint(
            model_name="invitationtoproject",
            constraint=models.UniqueConstraint(
                condition=models.Q(("status", 1)),
                fields=("user", "position"),
                name="projects_invitationtoproject_unique_request_per_project",
            ),
        ),
    ]
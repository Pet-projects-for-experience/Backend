# Generated by Django 5.0.1 on 2024-05-11 02:42

import apps.general.fields
import django.core.validators
import django.db.models.deletion
import re
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("projects", "0008_rename_is_favorite_project_favorited_by"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name="project",
            name="busyness",
            field=models.PositiveSmallIntegerField(
                choices=[(1, 10), (2, 20), (3, 30), (4, 40)],
                null=True,
                verbose_name="Занятость (час/нед)",
            ),
        ),
        migrations.AlterField(
            model_name="project",
            name="ended",
            field=models.DateField(null=True, verbose_name="Дата завершения"),
        ),
        migrations.AlterField(
            model_name="project",
            name="participants",
            field=models.ManyToManyField(
                related_name="projects_participated",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Участники",
            ),
        ),
        migrations.AlterField(
            model_name="project",
            name="started",
            field=models.DateField(null=True, verbose_name="Дата начала"),
        ),
        migrations.CreateModel(
            name="ParticipationRequest",
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
                "verbose_name": "Запрос на участие",
                "verbose_name_plural": "Запросы на участие",
                "default_related_name": "participation_requests",
            },
        ),
        migrations.AddConstraint(
            model_name="participationrequest",
            constraint=models.UniqueConstraint(
                condition=models.Q(("status", 1)),
                fields=("project", "user", "position"),
                name="projects_participationrequest_unique_request_per_project",
            ),
        ),
    ]
# Generated by Django 5.0.1 on 2025-01-06 11:38

import apps.general.fields
import django.core.validators
import re
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        (
            "projects",
            "0020_remove_invitationtoproject_projects_invitationtoproject_unique_request_per_project_and_more",
        ),
    ]

    operations = [
        migrations.AlterField(
            model_name="invitationtoproject",
            name="answer",
            field=apps.general.fields.BaseTextField(
                blank=True,
                max_length=750,
                null=True,
                validators=[
                    django.core.validators.RegexValidator(
                        flags=re.RegexFlag["IGNORECASE"],
                        message="Поле может содержать: кириллические и латинские символы, цифры и спецсимовлы -!#$%%&'*+/=?^_;():@,.<>`{}~«»",
                        regex="(^[-%!#$&*'+/=?^_;():@,.<>`{|}~\\\"\\\\\\-«»0-9A-ZА-ЯЁ\\s]+)\\Z",
                    ),
                    django.core.validators.MinLengthValidator(
                        limit_value=5,
                        message="Длина поля от 5 до 750 символов.",
                    ),
                ],
                verbose_name="Ответ",
            ),
        ),
        migrations.AlterField(
            model_name="participationrequest",
            name="answer",
            field=apps.general.fields.BaseTextField(
                blank=True,
                max_length=750,
                null=True,
                validators=[
                    django.core.validators.RegexValidator(
                        flags=re.RegexFlag["IGNORECASE"],
                        message="Поле может содержать: кириллические и латинские символы, цифры и спецсимовлы -!#$%%&'*+/=?^_;():@,.<>`{}~«»",
                        regex="(^[-%!#$&*'+/=?^_;():@,.<>`{|}~\\\"\\\\\\-«»0-9A-ZА-ЯЁ\\s]+)\\Z",
                    ),
                    django.core.validators.MinLengthValidator(
                        limit_value=5,
                        message="Длина поля от 5 до 750 символов.",
                    ),
                ],
                verbose_name="Ответ",
            ),
        ),
    ]
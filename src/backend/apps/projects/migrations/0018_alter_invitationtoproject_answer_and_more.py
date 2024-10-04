# Generated by Django 5.0.1 on 2024-10-04 21:05

import apps.general.fields
import django.core.validators
import re
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("projects", "0017_alter_project_participants"),
    ]

    operations = [
        migrations.AlterField(
            model_name="invitationtoproject",
            name="answer",
            field=apps.general.fields.BaseTextField(
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
            model_name="invitationtoproject",
            name="cover_letter",
            field=apps.general.fields.BaseTextField(
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
                verbose_name="Сопроводительное письмо",
            ),
        ),
        migrations.AlterField(
            model_name="participationrequest",
            name="answer",
            field=apps.general.fields.BaseTextField(
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
            name="cover_letter",
            field=apps.general.fields.BaseTextField(
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
                verbose_name="Сопроводительное письмо",
            ),
        ),
        migrations.AlterField(
            model_name="project",
            name="description",
            field=models.TextField(
                max_length=1500,
                null=True,
                validators=[
                    django.core.validators.MinLengthValidator(
                        limit_value=20,
                        message="Длина поля от 20 до 1500 символов.",
                    ),
                    django.core.validators.RegexValidator(
                        flags=re.RegexFlag["IGNORECASE"],
                        message="Описание может содержать: кириллические и латинские буквы, цифры и специальные символы.",
                        regex="(^[\\Wa-zа-яё0-9\\s]+)\\Z",
                    ),
                ],
                verbose_name="Описание",
            ),
        ),
        migrations.AlterField(
            model_name="project",
            name="name",
            field=models.CharField(
                max_length=100,
                validators=[
                    django.core.validators.MinLengthValidator(
                        limit_value=5,
                        message="Длина поля от 5 до 100 символов.",
                    ),
                    django.core.validators.RegexValidator(
                        message="Название проекта может содержать: кириллические и латинские символы, цифры и символы .,-—+_/:",
                        regex="(^[+/_:,.0-9A-Za-zА-Яа-яЁё\\s\\-–—]+)\\Z",
                    ),
                ],
                verbose_name="Название",
            ),
        ),
    ]

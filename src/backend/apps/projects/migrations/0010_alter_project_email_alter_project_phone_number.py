# Generated by Django 5.0.1 on 2024-05-17 16:39

import apps.general.fields
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        (
            "projects",
            "0009_alter_project_busyness_alter_project_ended_and_more",
        ),
    ]

    operations = [
        migrations.AlterField(
            model_name="project",
            name="email",
            field=apps.general.fields.CustomEmailField(
                blank=True,
                max_length=256,
                null=True,
                verbose_name="Email address",
            ),
        ),
        migrations.AlterField(
            model_name="project",
            name="phone_number",
            field=models.TextField(
                blank=True,
                max_length=12,
                null=True,
                validators=[
                    django.core.validators.RegexValidator(
                        message="Допустимый формат +7XXXXXXXXXX, где X - цифры.",
                        regex="^\\+7\\d{10}$",
                    )
                ],
                verbose_name="Номер телефона",
            ),
        ),
    ]
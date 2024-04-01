# Generated by Django 5.0.1 on 2024-03-27 19:19

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("general", "0002_alter_specialist_specialization_and_more"),
        ("projects", "0002_alter_project_busyness"),
    ]

    operations = [
        migrations.AlterField(
            model_name="direction",
            name="name",
            field=models.CharField(
                max_length=20,
                unique=True,
                validators=[
                    django.core.validators.MinLengthValidator(
                        limit_value=2,
                        message="Длина поля от 2 до 20 символов.",
                    ),
                    django.core.validators.RegexValidator(
                        message="Направление разработки может содержать: кириллические и латинские символы.",
                        regex="(^[A-Za-zА-Яа-яЁё]+)\\Z",
                    ),
                ],
                verbose_name="Название",
            ),
        ),
        migrations.AddConstraint(
            model_name="projectspecialist",
            constraint=models.UniqueConstraint(
                fields=("project", "specialist", "level"),
                name="projects_projectspecialist_unique_specialist_per_project",
            ),
        ),
    ]

# Generated by Django 5.0.1 on 2024-10-04 21:05

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("profile", "0008_alter_profile_portfolio_link"),
    ]

    operations = [
        migrations.AlterField(
            model_name="profile",
            name="about",
            field=models.TextField(
                blank=True,
                max_length=1500,
                validators=[
                    django.core.validators.RegexValidator(
                        message="Введите кириллицу или латиницу",
                        regex="(^[\\Wa-zа-яё0-9\\s]+)\\Z",
                    ),
                    django.core.validators.MinLengthValidator(limit_value=20),
                ],
                verbose_name="О себе",
            ),
        ),
    ]
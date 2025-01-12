# Generated by Django 5.0.1 on 2024-06-23 07:55

import apps.general.fields
import django.core.validators
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("profile", "0007_alter_profile_portfolio_link"),
    ]

    operations = [
        migrations.AlterField(
            model_name="profile",
            name="portfolio_link",
            field=apps.general.fields.CustomURLField(
                blank=True,
                max_length=256,
                validators=[
                    django.core.validators.MinLengthValidator(
                        limit_value=5,
                        message="Длинна URL-адреса должна быть от 5 до 256 символов.",
                    )
                ],
                verbose_name="Ссылка на портфолио",
            ),
        ),
    ]

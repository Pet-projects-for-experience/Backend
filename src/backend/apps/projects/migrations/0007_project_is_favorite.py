# Generated by Django 5.0.1 on 2024-05-03 10:17

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("projects", "0006_alter_projectspecialist_level"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="project",
            name="is_favorite",
            field=models.ManyToManyField(
                blank=True,
                related_name="favorite_projects",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Добавили в избранное",
            ),
        ),
    ]
# Generated by Django 5.0.1 on 2024-05-06 07:09

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("projects", "0007_project_is_favorite"),
    ]

    operations = [
        migrations.RenameField(
            model_name="project",
            old_name="is_favorite",
            new_name="favorited_by",
        ),
    ]
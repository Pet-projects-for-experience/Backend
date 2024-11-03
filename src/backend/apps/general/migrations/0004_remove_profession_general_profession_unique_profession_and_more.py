# Generated by Django 5.0.1 on 2024-10-30 20:04

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("general", "0003_rename_specialist_profession_and_more"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="profession",
            name="general_profession_unique_profession",
        ),
        migrations.RenameField(
            model_name="profession",
            old_name="specialty",
            new_name="speciality",
        ),
        migrations.AddConstraint(
            model_name="profession",
            constraint=models.UniqueConstraint(
                fields=("speciality", "specialization"),
                name="general_profession_unique_profession",
            ),
        ),
    ]

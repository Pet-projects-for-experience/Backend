# Generated by Badmajor 5.0.1 on 2024-10-24 23:55

from django.contrib.postgres.operations import TrigramExtension
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("profile", "0009_alter_profile_about"),
    ]

    operations = [
        TrigramExtension(),
    ]

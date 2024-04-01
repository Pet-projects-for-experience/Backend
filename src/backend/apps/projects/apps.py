from django.apps import AppConfig


class ProjectConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.projects"

    def ready(self):
        from . import signals  # noqa: F401,

        return super().ready()

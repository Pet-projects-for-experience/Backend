from django.apps import AppConfig
from django.core.signals import request_finished


class UsersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.users"

    def ready(self):
        from api.v1.profile import signals

        request_finished.connect(signals.create_user_profile)

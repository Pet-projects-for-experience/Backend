from .base import *  # noqa

DEBUG = getenv("DEBUG", default="True") == "True"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory",  # Создаем базу в памяти, должно ускорить выполнение тестов
    }
}
LOGGING["loggers"].pop("django.db.backends", None)
LOGGING["loggers"]["django"]["level"] = "WARNING"

setup_logging()

from .base import *  # noqa

DEBUG = True

EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
EMAIL_PORT = 587

CORS_ALLOWED_ORIGINS = [
    "https://89.23.117.80",
    "https://devcodepet.tw1.ru",
    "http://localhost:3000",
]

CSRF_TRUSTED_ORIGINS = [
    "https://89.23.117.80",
    "https://devcodepet.tw1.ru",
]


LOGGING["loggers"].pop("django.db.backends", None)
LOGGING["loggers"]["django"]["level"] = "WARNING"

setup_logging()

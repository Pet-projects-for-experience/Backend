from .base import *  # noqa

DEBUG = False


EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
EMAIL_PORT = 587

CORS_ALLOWED_ORIGINS = [
    "https://89.23.117.168",
    "https://testcodepet.tw1.ru",
    "http://localhost:3000",
]

LOGGING["loggers"].pop("django.db.backends", None)
LOGGING["loggers"]["django"]["level"] = "WARNING"

setup_logging()

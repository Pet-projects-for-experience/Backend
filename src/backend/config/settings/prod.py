from .base import *  # noqa

DEBUG = False
SERVER_HOST = getenv("SERVER_HOST_QA")
SERVER_NAME = getenv("SERVER_NAME_QA")


EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
EMAIL_PORT = 587

CORS_ALLOWED_ORIGINS = [
    f"http://{SERVER_HOST}",
    f"https://{SERVER_NAME}",
    "http://localhost:3000",
]

CSRF_TRUSTED_ORIGINS = [
    f"http://{SERVER_HOST}",
    f"https://{SERVER_NAME}",
    "http://localhost:8000",
]


LOGGING["loggers"].pop("django.db.backends", None)
LOGGING["loggers"]["django"]["level"] = "WARNING"

setup_logging()

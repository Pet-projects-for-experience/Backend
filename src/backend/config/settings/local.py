from .base import *  # noqa

DEBUG = getenv("DEBUG", default="True") == "True"

if getenv("USE_SQLITE", default="True") == "True":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": str(BASE_DIR / "db.sqlite3"),
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": getenv(
                "DB_ENGINE", default="django.db.backends.postgresql"
            ),
            "NAME": getenv("POSTGRES_DB", default="db_test"),
            "USER": getenv("POSTGRES_USER", default="admin_test"),
            "PASSWORD": getenv("POSTGRES_PASSWORD", default="postgre_admin"),
            "HOST": getenv("POSTGRES_HOST", default="db_test"),
            "PORT": getenv("POSTGRES_PORT", default=5432),
        }
    }

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# LOGGING = {
#     "version": 1,
#     "disable_existing_loggers": False,
#     "formatters": {
#         "verbose": {
#             "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
#         },
#     },
#     "handlers": {
#         "console": {
#             "class": "logging.StreamHandler",
#             "formatter": "verbose",
#         },
#     },
#     "loggers": {
#         "django": {
#             "level": "INFO",
#             "handlers": [
#                 "console",
#             ],
#         },
#         "django.db.backends": {
#             "level": "DEBUG",
#             "handlers": [
#                 "console",
#             ],
#             "propagate": False,
#         },
#     },
# }

LOGGING["handlers"].pop("file", None)
LOGGING["handlers"].pop("mail_admins", None)
LOGGING["loggers"].pop("django.request", None)
LOGGING["loggers"].pop("django.request", None)
LOGGING["loggers"].pop("django.security", None)
LOGGING["loggers"].pop("django.security.csrf", None)
LOGGING["loggers"].pop("customlogger", None)
LOGGING["loggers"]["django"]["level"] = ["INFO"]

setup_logging()

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
]

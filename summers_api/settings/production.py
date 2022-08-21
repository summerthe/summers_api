import boto3

from .base import *  # noqa: F401,F403
from .base import (
    AWS_ACCESS_KEY_ID,
    AWS_DEFAULT_REGION,
    AWS_S3_ORIGIN,
    AWS_SECRET_ACCESS_KEY,
    BASE_DIR,
)

cloudwatch_boto3_client = boto3.client(
    "logs",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_DEFAULT_REGION,
)
# Save only two log files of max 20 mb.
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "root": {"level": "INFO", "handlers": ["file"]},
    "handlers": {
        "file": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": ".django.log",
            "formatter": "app",
            "backupCount": 1,
            "maxBytes": 20 * 1024 * 1024,  # 20*1024*1024 bytes (20MB)
        },
        "watchtower": {
            "level": "DEBUG",
            "class": "watchtower.CloudWatchLogHandler",
            "boto3_client": cloudwatch_boto3_client,
            "log_group": "summersapi",
            "stream_name": "default",
            "formatter": "aws",
        },
    },
    "loggers": {
        "django": {"handlers": ["file"], "level": "INFO", "propagate": True},
        "aws": {
            "level": "DEBUG",
            "handlers": ["watchtower"],
            "propagate": False,
        },
    },
    "formatters": {
        "app": {
            "format": (
                "%(asctime)s [%(levelname)s]" "(%(module)s.%(funcName)s) %(message)s"
            ),
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "aws": {
            "format": "%(asctime)s [%(levelname)s]"
            "(%(module)s.%(funcName)s) %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
}

DEBUG = False

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
STATIC_URL = AWS_S3_ORIGIN + "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

WHITENOISE_MANIFEST_STRICT = False

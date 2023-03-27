import boto3

from .base import *  # noqa: F401,F403
from .base import (
    AWS_ACCESS_KEY_ID,
    AWS_DEFAULT_REGION,
    AWS_S3_BUCKET,
    AWS_S3_ORIGIN,
    AWS_SECRET_ACCESS_KEY,
    AWS_USE_S3_STATIC,
    BASE_DIR,
    INSTALLED_APPS,
    SWAGGER_SETTINGS,
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
    # "root": {"level": "INFO", "handlers": ["file"]},
    "handlers": {
        # "file": {
        #     "level": "INFO",
        #     "class": "logging.handlers.RotatingFileHandler",
        #     "filename": ".django.log",
        #     "formatter": "app",
        #     "backupCount": 1,
        #     "maxBytes": 20 * 1024 * 1024,  # 20*1024*1024 bytes (20MB)
        # },
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
        # "django": {"handlers": ["file"], "level": "INFO", "propagate": True},
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

STATIC_URL = AWS_S3_ORIGIN + "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# s3 static settings
if AWS_USE_S3_STATIC:
    AWS_DEFAULT_ACL = "public-read"
    AWS_STORAGE_BUCKET_NAME = AWS_S3_BUCKET
    AWS_S3_OBJECT_PARAMETERS = {"CacheControl": "max-age=86400"}
    AWS_LOCATION = "static"
    STATICFILES_STORAGE = "storages.backends.s3boto3.S3ManifestStaticStorage"
    INSTALLED_APPS += ["storages"]
    AWS_S3_CUSTOM_DOMAIN = AWS_S3_ORIGIN.replace(r"https://", "")
else:
    WHITENOISE_MANIFEST_STRICT = False
    STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

SWAGGER_SETTINGS["DEFAULT_GENERATOR_CLASS"] = "apps.common.swagger.HttpsSchemaGenerator"

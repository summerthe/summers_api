from .base import *  # noqa: F401,F403

# Save only two log files of max 5 mb.
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
            "maxBytes": 5 * 1024 * 1024,  # 5*1024*1024 bytes (5MB)
        },
    },
    "loggers": {
        "django": {"handlers": ["file"], "level": "INFO", "propagate": True},
    },
    "formatters": {
        "app": {
            "format": (
                "%(asctime)s [%(levelname)s]" "(%(module)s.%(funcName)s) %(message)s"
            ),
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
}

DEBUG = False

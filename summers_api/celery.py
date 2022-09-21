from pathlib import Path

import environ
from celery import Celery

# Build paths inside the project like this: BASE_DIR / 'subdir'.
# Reading env to set `DJANGO_SETTINGS_MODULE`
BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env()
env.read_env(str(BASE_DIR / ".env"))

app = Celery("summers_api")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

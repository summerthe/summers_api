"""ASGI config for summers_api project.

It exposes the ASGI callable as a module-level variable named ``application``.
For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/asgi/
"""
from pathlib import Path

import environ
from django.core.asgi import get_asgi_application

# Build paths inside the project like this: BASE_DIR / 'subdir'.
# Reading env to set `DJANGO_SETTINGS_MODULE`
BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env()
env.read_env(str(BASE_DIR / ".env"))

application = get_asgi_application()

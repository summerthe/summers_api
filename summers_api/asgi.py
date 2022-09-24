"""ASGI config for summers_api project.

It exposes the ASGI callable as a module-level variable named ``application``.
For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/asgi/
"""
from pathlib import Path

import environ
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application

from apps.tube2drive import routing as tube2drive_websocket_routing

# Build paths inside the project like this: BASE_DIR / 'subdir'.
# Reading env to set `DJANGO_SETTINGS_MODULE`
BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env()
env.read_env(str(BASE_DIR / ".env"))

django_asgi_app = get_asgi_application()

# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may import ORM models.
application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AllowedHostsOriginValidator(
            AuthMiddlewareStack(
                URLRouter(tube2drive_websocket_routing.websocket_urlpatterns),
            ),
        ),
    },
)

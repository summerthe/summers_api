from channels.routing import URLRouter
from django.urls import path

from apps.tube2drive import consumers

_url_router = URLRouter(
    [
        path(
            "upload-requests/<uuid:user_uuid>/",
            consumers.UploadRequestUpdateConsumer.as_asgi(),
        ),
    ],
)

websocket_urlpatterns = [path("tube2drive/", _url_router)]

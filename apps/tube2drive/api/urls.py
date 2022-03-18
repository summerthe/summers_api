from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter

from . import views

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()  # type: ignore

app_name = "apps.tube2drive"

router.register(
    "upload-requests",
    views.UploadRequestViewSet,
    basename="upload-requests",
)
urlpatterns = router.urls

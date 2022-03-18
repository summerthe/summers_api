from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter

from apps.users.api import views

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

app_name = "apps.users"

router.register("auth", views.AuthViewSet)
urlpatterns = router.urls

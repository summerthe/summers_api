from django.conf import settings
from django.urls.conf import include, path
from rest_framework.routers import DefaultRouter, SimpleRouter

from apps.users.api import views

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()  # type: ignore

app_name = "apps.users"

router.register("auth", views.AuthViewSet)
urlpatterns = router.urls

urlpatterns += [
    path("auth/login/", include("rest_social_auth.urls_jwt_pair")),
]

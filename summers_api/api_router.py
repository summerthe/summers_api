from django.conf import settings
from django.urls.conf import include, path
from rest_framework.routers import DefaultRouter, SimpleRouter

if settings.DEBUG:
    router: DefaultRouter | SimpleRouter = DefaultRouter()
else:
    router = SimpleRouter()

app_name = "api"
urlpatterns = [
    path("", include("apps.users.api.urls")),
    path("tube2drive/", include("apps.tube2drive.api.urls")),
    path("news/", include("apps.news.api.urls")),
    # unpacking `URLResolver`, could write `[] + router.urls`,
    # but this unpacking is preferred to fix type hint error between `URLPattern + URLResolver`
    *router.urls,
]

from django.conf import settings
from django.urls import re_path
from django.urls.conf import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework.routers import DefaultRouter, SimpleRouter

if settings.DEBUG:
    router: DefaultRouter | SimpleRouter = DefaultRouter()
else:
    router = SimpleRouter()

schema_view = get_schema_view(
    openapi.Info(
        title="Summers API",
        default_version="v1",
        description="List of all public APIs of v1.",
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)


app_name = "api"
urlpatterns = [
    path("", include("apps.users.api.urls")),
    path("tube2drive/", include("apps.tube2drive.api.urls")),
    path("news/", include("apps.news.api.urls")),
    # Swagger paths
    re_path(
        r"^swagger(?P<format>\.json|\.yaml)$",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
    path("swagger", schema_view.with_ui("swagger"), name="schema-swagger-ui"),
    path("redoc", schema_view.with_ui("redoc"), name="schema-redoc"),
    # unpacking `URLResolver`, could write `[] + router.urls`,
    # but this unpacking is preferred to fix type hint error between `URLPattern + URLResolver`
    *router.urls,
]

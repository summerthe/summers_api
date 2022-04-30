from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter

from . import views

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()  # type: ignore

app_name = "apps.news"

router.register(
    "newsletter",
    views.NewsletterViewSet,
    basename="newsletter",
)
router.register(
    "categories",
    views.CategoryViewSet,
    basename="categories",
)
router.register(
    "weather",
    views.WeatherViewSet,
    basename="weather",
)

urlpatterns = router.urls

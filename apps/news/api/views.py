import pandas as pd
import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response

from apps.base.apis import viewsets
from apps.news.api.serializers import (
    CategorySerializer,
    NewsletterSerializer,
    SavedArticleSerializer,
)
from apps.news.models import Category, Newsletter, SavedArticle

User = get_user_model()


class NewsletterViewSet(viewsets.GenericViewSet):
    """Following Endpoints are created by this modelviewset.

    Subscribe: POST `/subscribe/`
    Unsubscribe: POST `/unsubscribe/`
    """

    queryset = Newsletter.objects.all()
    serializer_class = NewsletterSerializer

    @action(detail=False, methods=["post"], url_path="subscribe")
    def subscribe(self, request: Request, *args, **kwargs):
        """Subscriber current user for newsletter."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            newsletter = Newsletter.objects.get(user=self.request.user)
        except Newsletter.DoesNotExist:
            newsletter = serializer.save()

        return Response(
            NewsletterSerializer(instance=newsletter).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=["post"], url_path="unsubscribe")
    def unsubscribe(self, request: Request, *args, **kwargs):
        """Unsubscriber current user for newsletter."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        newsletter = get_object_or_404(Newsletter, user=self.request.user)
        newsletter.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CategoryViewSet(viewsets.BaseListRetrieveModelViewSet):
    """Following Endpoints are created by this modelviewset.

    List : GET `/`
    Get : GET `/<pk>/`
    """

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (AllowAny,)


class WeatherViewSet(viewsets.GenericViewSet):
    """Following Endpoints are created by this modelviewset.

    Get weather: GET `/get-temp/`
    """

    permission_classes = (AllowAny,)

    @action(detail=False, methods=["get"], url_path="get-temp")
    def get_temp(self, request: Request, *args, **kwargs):
        """Get weather data from ip address."""

        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")

        if x_forwarded_for:
            ip_address = x_forwarded_for.split(",")[0]
        else:
            ip_address = request.META.get("REMOTE_ADDR")

        latlong = requests.get(
            f"https://ipapi.co/{ip_address}/latlong/",
        ).text.split(",")

        OPENWEATHER_API_KEY = settings.OPENWEATHER_API_KEY

        weather = requests.get(
            f"""http://api.openweathermap.org/data/2.5/weather?lat={latlong[0]}&lon={latlong[1]}&appid={
                OPENWEATHER_API_KEY}""",
        ).json()

        return Response(
            data=weather,
            status=status.HTTP_200_OK,
        )


class SavedArticleViewSet(viewsets.BaseCreateListRetrieveModelViewSet):
    """Following Endpoints are created by this modelviewset.

    Create: POST `/`
    List: GET `/`
    Get: GET `/<pk>/`
    """

    queryset = SavedArticle.objects.all()
    serializer_class = SavedArticleSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(user=self.request.user)


class ArticleViewSet(viewsets.GenericViewSet):
    """Following Endpoints are created by this modelviewset.

    List: GET `/`
    """

    permission_classes = (AllowAny,)

    def list(self, request):
        NEWSDATA_IO_API_KEY = settings.NEWSDATA_IO_API_KEY
        base_url = (
            f"https://newsdata.io/api/1/news?apikey={NEWSDATA_IO_API_KEY}&language=en"
        )

        if query := self.request.GET.get("q"):
            base_url += f"&q={query}"

        if category := self.request.GET.get("category"):
            base_url += f"&category={category.lower()}"

        if to_date := self.request.GET.get("to_date"):
            base_url += f"&to_date={to_date}"

        if from_date := self.request.GET.get("from_date"):
            base_url += f"&from_date={from_date}"

        if page := self.request.GET.get("page"):
            base_url += f"&page={page}"

        response = requests.get(base_url)
        data = response.json()

        # convert empty image_url to default image.
        results_df = pd.DataFrame(data["results"])

        if len(results_df) > 0:
            results_df["image_url"] = results_df["image_url"].fillna(
                settings.DEFAULT_NEWS_IMAGE_URL,
            )
            data["results"] = results_df.to_dict("records")

        return Response(data=data, status=status.HTTP_200_OK)

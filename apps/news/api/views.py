from typing import Any

import pandas as pd
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models.query import QuerySet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer

from apps.base.apis import viewsets
from apps.common.utils.async_request import AsyncRequest, ResponseType
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
    def subscribe(self, request: Request, *args, **kwargs) -> Response:
        """Subscriber current logged user for newsletter.

        Parameters
        ----------
        request : Request

        Returns
        -------
        Response
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            # if newsletter doesn't exist create new for current logged user.
            newsletter = Newsletter.objects.get(user=self.request.user)  # type: ignore[misc]
        except Newsletter.DoesNotExist:
            newsletter = serializer.save()

        return Response(
            NewsletterSerializer(instance=newsletter).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=["post"], url_path="unsubscribe")
    def unsubscribe(self, request: Request, *args, **kwargs) -> Response:
        """Unsubscribes current logged user for newsletter.

        Parameters
        ----------
        request : Request

        Returns
        -------
        Response
        """
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

    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Returns all news categories.

        Parameters
        ----------
        request : Request

        Returns
        -------
        Response
        """
        return super().list(request, *args, **kwargs)

    def retrieve(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Retrieves single news category.

        Parameters
        ----------
        request : Request

        Returns
        -------
        Response
        """
        return super().retrieve(request, *args, **kwargs)


class WeatherViewSet(viewsets.GenericViewSet):
    """Following Endpoints are created by this modelviewset.

    Get weather: GET `/get-temp/`
    """

    permission_classes = (AllowAny,)
    # providing serializer_class for not using serializer
    # in generic functions.
    serializer_class = BaseSerializer

    @action(detail=False, methods=["get"], url_path="get-temp")
    def get_temp(self, request: Request, *args, **kwargs) -> Response:
        """Get weather data from ip address.

        Parameters
        ----------
        request : Request

        Returns
        -------
        Response
        """
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")

        if x_forwarded_for:
            ip_address = x_forwarded_for.split(",")[0]
        else:
            ip_address = request.META.get("REMOTE_ADDR")

        lat_long = AsyncRequest.run_async(
            AsyncRequest.get(f"https://ipapi.co/{ip_address}/latlong/"),
        ).split(",")

        OPEN_WEATHER_API_KEY = settings.OPEN_WEATHER_API_KEY

        weather = AsyncRequest.run_async(
            AsyncRequest.get(
                f"""http://api.openweathermap.org/data/2.5/weather?lat={lat_long[0]}&lon={lat_long[1]}&appid={
                OPEN_WEATHER_API_KEY}""",
                ResponseType.json,
            ),
        )

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

    def get_queryset(self) -> QuerySet[SavedArticle]:
        """Filters SavedArticle for current logged user.

        Returns
        -------
        QuerySet[SavedArticle]
        """
        qs = super().get_queryset()
        if self.request.user.is_authenticated:
            qs = qs.filter(user=self.request.user)
        return qs

    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Save `https://newsdata.io` article.

        Parameters
        ----------
        request : Request

        Returns
        -------
        Response
        """
        return super().create(request, *args, **kwargs)

    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Returns list of saved articles of user.

        Parameters
        ----------
        request : Request

        Returns
        -------
        Response
        """
        return super().list(request, *args, **kwargs)

    def retrieve(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Retrieves single saved article of user.

        Parameters
        ----------
        request : Request

        Returns
        -------
        Response
        """
        return super().retrieve(request, *args, **kwargs)


class ArticleViewSet(viewsets.GenericViewSet):
    """Following Endpoints are created by this modelviewset.

    List: GET `/`
    """

    permission_classes = (AllowAny,)
    # providing serializer_class for not using serializer
    # in generic functions.
    serializer_class = BaseSerializer

    def list(self, request: Request, *args, **kwargs) -> Response:
        """Fetch Article from `https://newsdata.io` API.

        Parameters
        ----------
        request : Request

        Returns
        -------
        Response
        """
        NEWS_DATA_IO_API_KEY = settings.NEWS_DATA_IO_API_KEY
        base_url = (
            f"https://newsdata.io/api/1/news?apikey={NEWS_DATA_IO_API_KEY}&language=en"
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

        data = AsyncRequest.run_async(
            AsyncRequest.get(
                base_url,
                ResponseType.json,
            ),
        )

        # convert empty image_url to default image.
        results_df = pd.DataFrame(data["results"])

        if len(results_df) > 0:
            results_df["image_url"] = results_df["image_url"].fillna(
                settings.DEFAULT_NEWS_IMAGE_URL,
            )
            data["results"] = results_df.to_dict("records")

        return Response(data=data, status=status.HTTP_200_OK)

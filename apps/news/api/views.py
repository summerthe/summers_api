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
from apps.news.api.serializers import CategorySerializer, NewsletterSerializer
from apps.news.models import Category, Newsletter

User = get_user_model()


class NewsletterViewSet(viewsets.GenericViewSet):
    """
    Following Endpoints are created by this modelviewset.

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
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (AllowAny,)


class WeatherViewSet(viewsets.GenericViewSet):
    permission_classes = (AllowAny,)

    @action(detail=False, methods=["get"], url_path="get-temp")
    def get_weather(self, request: Request, *args, **kwargs):
        """Get weather data from ip address."""

        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")

        if x_forwarded_for:
            ip_address = x_forwarded_for.split(",")[0]
        else:
            ip_address = request.META.get("REMOTE_ADDR")
        print("ip_address", ip_address)
        latlong = requests.get(
            "https://ipapi.co/{}/latlong/".format(ip_address)
        ).text.split(",")

        OPENWEATHER_API_KEY = settings.OPENWEATHER_API_KEY

        weather = requests.get(
            f"""http://api.openweathermap.org/data/2.5/weather?lat={latlong[0]}&lon={latlong[1]}&appid={
                OPENWEATHER_API_KEY}"""
        ).json()

        return Response(
            data=weather,
            status=status.HTTP_201_CREATED,
        )

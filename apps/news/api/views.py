from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.request import Request
from rest_framework.response import Response

from apps.base.apis import viewsets
from apps.news.api.serializers import NewsletterSerializer
from apps.news.models import Newsletter

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

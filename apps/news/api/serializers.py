from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.news.models import Newsletter

User = get_user_model()


class NewsletterSerializer(serializers.ModelSerializer):
    """Serializer for read and create requests."""

    class Meta:
        model = Newsletter
        fields = "__all__"
        read_only_fields = (
            "id",
            "user",
        )

    def save(self, **kwargs):
        request = self.context.get("request")
        user = request.user  # type: ignore
        return super().save(user=user)

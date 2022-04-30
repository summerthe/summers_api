from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.news.models import Category, Newsletter, SavedArticle

User = get_user_model()


class NewsletterSerializer(serializers.ModelSerializer):
    """Serializer for read and create newsletters."""

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


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for read categories."""

    class Meta:
        model = Category
        fields = "__all__"


class SavedArticleSerializer(serializers.ModelSerializer):
    """Serializer for read and create Saved Articles."""

    class Meta:
        model = SavedArticle
        fields = "__all__"
        read_only_fields = (
            "id",
            "user",
        )

    def save(self, **kwargs):
        request = self.context.get("request")
        user = request.user  # type: ignore
        return super().save(user=user)

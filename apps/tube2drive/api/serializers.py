from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.tube2drive.models import UploadRequest

User = get_user_model()


class UploadRequestSerializer(serializers.ModelSerializer):
    """Serializer for read and create requests."""

    class Meta:
        model = UploadRequest
        fields = "__all__"
        read_only_fields = (
            "id",
            "status",
            "user",
            "unique_identifier",
            "slug",
        )

    def save(self, **kwargs) -> UploadRequest:
        """Save current logged user for user field.

        Returns
        -------
        UploadRequest
        """
        request = self.context.get("request")
        user = request.user if hasattr(request, "user") else None  # type: ignore[union-attr]
        return super().save(user=user)


class UploadRequestUpdateStatusSerializer(serializers.ModelSerializer):
    """Serializer to update request status."""

    class Meta:
        model = UploadRequest
        fields = ("status",)

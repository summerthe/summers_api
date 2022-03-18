from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializers for read requests."""

    class Meta:
        model = User
        exclude = (
            "is_active",
            "is_staff",
            "date_joined",
            "last_login",
            "password",
            "is_superuser",
            "groups",
            "user_permissions",
        )


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer to create user.

    Not need of confirm password, should be cleaned at frontend.
    """

    class Meta:
        model = User
        fields = ("name", "email", "password")

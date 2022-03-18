from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
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
    class Meta:
        model = User
        fields = ("name", "email", "password")

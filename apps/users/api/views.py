import ast
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import exceptions, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer,
    TokenRefreshSerializer,
)
from base.apis import viewsets
from apps.users.api.serializers import UserCreateSerializer, UserSerializer

User = get_user_model()


class AuthViewSet(viewsets.BaseCreateModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def get_serializer_class(self, *args, **kwargs):
        if self.action == "create":
            return UserCreateSerializer
        elif self.action == "login":
            return TokenObtainPairSerializer
        elif self.action == "refresh_token":
            return TokenRefreshSerializer
        return super().get_serializer_class(*args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            validate_password(password=serializer.validated_data["password"])
        except ValidationError as err:
            raise exceptions.ValidationError(
                detail={"password": ast.literal_eval(str(err))}
            )

        user = serializer.save()
        user.set_password(serializer.validated_data["password"])
        user.save()

        headers = self.get_success_headers(serializer.data)
        return Response(
            UserSerializer(instance=user).data,
            status=status.HTTP_201_CREATED,
            headers=headers,
        )

    @action(detail=False, methods=["post"], url_path="login")
    def login(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        data = serializer.validated_data
        data["user"] = UserSerializer(serializer.user).data
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="refresh-token")
    def refresh_token(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        return Response(serializer.validated_data, status=status.HTTP_200_OK)

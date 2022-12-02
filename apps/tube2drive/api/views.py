from typing import Any, Type

from django.contrib.auth import get_user_model
from django.db.models.query import QuerySet
from rest_framework import status
from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer

from apps.base.apis import viewsets
from apps.base.apis.permissions import AppOwnPermission
from apps.tube2drive.api.serializers import (
    UploadRequestSerializer,
    UploadRequestUpdateStatusSerializer,
)
from apps.tube2drive.models import UploadRequest

User = get_user_model()


class UploadRequestViewSet(viewsets.BaseModelViewSet):
    """Following Endpoints are created by this modelviewset.

    Create: POST `/`
    List: GET `/`
    Retrieve: GET `/<pk>/`
    Update: PUT `/<pk>/` Update is only used internally.
    Delete: DELETE `/<pk>/`
    """

    queryset = UploadRequest.objects.all()
    serializer_class = UploadRequestSerializer

    def get_permissions(self) -> list[BasePermission]:  # type: ignore[override]
        """Permission class for UploadRequest APIs.

        Allow `update` permission for internal.
        Update API is not called by frontend.

        Returns
        -------
        list[BasePermission]
        """
        if self.action == "update":
            return [AppOwnPermission()]
        return super().get_permissions()  # type: ignore[return-value]

    def get_serializer_class(self, *args, **kwargs) -> Type[BaseSerializer]:
        """Serializer class for UploadRequest APIs.

        During `update` allow only status update by only internal.
        Update API is not called by frontend.

        Returns
        -------
        Type[BaseSerializer]
        """
        if self.action == "update":
            return UploadRequestUpdateStatusSerializer
        return super().get_serializer_class(*args, **kwargs)

    def get_queryset(self) -> QuerySet[UploadRequest]:
        """Filters UploadRequest for current logged user.

        For update doesn't filter any.

        Returns
        -------
        QuerySet[UploadRequest]
        """
        qs = super().get_queryset()
        if self.action == "update":
            return qs

        if self.request.user.is_authenticated:
            qs = qs.filter(user=self.request.user)
        return qs

    def update(self, request: Request, *args, **kwargs) -> Response:
        """Update UploadRequest status internally.

        This API is not called by frontend.

        Parameters
        ----------
        request : Request

        Returns
        -------
        Response
        """
        super().update(request, *args, **kwargs)
        instance = self.get_object()
        return Response(
            UploadRequestSerializer(instance).data,
            status=status.HTTP_200_OK,
        )

    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Create new upload request.

        Parameters
        ----------
        request : Request

        Returns
        -------
        Response
        """
        return super().create(request, *args, **kwargs)

    def retrieve(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Retrieves single upload requests for user.

        Parameters
        ----------
        request : Request

        Returns
        -------
        Response
        """
        return super().retrieve(request, *args, **kwargs)

    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Returns list of upload requests for user.

        Parameters
        ----------
        request : Request

        Returns
        -------
        Response
        """
        return super().list(request, *args, **kwargs)

    def destroy(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Delete upload request created by user.

        Parameters
        ----------
        request : Request

        Returns
        -------
        Response
        """
        return super().destroy(request, *args, **kwargs)

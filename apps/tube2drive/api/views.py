from django.contrib.auth import get_user_model
from rest_framework.request import Request
from rest_framework.response import Response

from apps.base.apis import viewsets
from apps.base.apis.permissions import AppOwnPermission
from apps.tube2drive.api.serializers import (
    UploadRequestSerializer,
    UploadRequestUpdateStatusSerializer,
)
from apps.tube2drive.models import UploadRequest

User = get_user_model()


class UploadRequestViewSet(viewsets.BaseModelViewSet):
    """
    Following Endpoints are created by this modelviewset.

    Create: POST `/`
    List: GET `/`
    Retrieve: GET `/<pk>/`
    Update: PUT `/<pk>/` Update is only used internally.
    Delete: DELETE `/<pk>/`
    """

    queryset = UploadRequest.objects.all()
    serializer_class = UploadRequestSerializer

    def get_permissions(self):
        if self.action == "update":
            return [AppOwnPermission()]
        return super().get_permissions()

    def get_serializer_class(self, *args, **kwargs):
        if self.action == "update":
            return UploadRequestUpdateStatusSerializer
        return super().get_serializer_class(*args, **kwargs)

    def get_queryset(self):
        qs = super().get_queryset()
        if self.action == "update":
            return qs
        qs = qs.filter(user=self.request.user)
        return qs

    def update(self, request: Request, *args, **kwargs):
        super().update(request, *args, **kwargs)
        instance = self.get_object()
        return Response(UploadRequestSerializer(instance).data)

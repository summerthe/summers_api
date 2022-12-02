from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet


class BaseModelViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    # not adding `patch`, instead use `put`
    http_method_names = ["get", "post", "head", "put", "delete"]


class BaseCreateModelViewSet(
    mixins.CreateModelMixin,
    GenericViewSet,
):
    pass


class BaseListModelViewSet(
    mixins.ListModelMixin,
    GenericViewSet,
):
    pass


class BaseRetrieveModelViewSet(
    mixins.RetrieveModelMixin,
    GenericViewSet,
):
    pass


class BaseUpdateModelViewSet(
    mixins.UpdateModelMixin,
    GenericViewSet,
):
    pass


class BaseDestroyModelViewSet(
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    pass


class BaseListRetrieveModelViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet,
):
    pass


class BaseListUpdateModelViewSet(
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    pass


class BaseListDestroyModelViewSet(
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    pass


class BaseCreateListRetrieveModelViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet,
):
    pass


class BaseCreateListRetrieveUpdateModelViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    GenericViewSet,
):
    pass

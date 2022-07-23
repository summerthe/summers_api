import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _


class BaseModel(models.Model):
    """Abstract model with create, update time and uuid fields."""

    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, auto_now_add=False)
    unique_identifier = models.UUIDField(
        _("Unique Identifier"),
        default=uuid.uuid4,
        editable=False,
    )

    class Meta:
        abstract = True

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.base.models import BaseModel


class User(AbstractUser, BaseModel):
    """Default user for Summers API."""

    last_name = first_name = None  # type: ignore[assignment]
    username = None  # type: ignore[assignment]

    name = models.CharField(_("Name"), max_length=255)
    email = models.EmailField(_("Email address"), unique=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS: list[str] = []

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        ordering = ["-updated_at"]

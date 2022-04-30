from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext as _

from apps.base.models import BaseModel

User = get_user_model()


class Newsletter(BaseModel):
    """Weekly Newsletter subscibered users."""

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.user)

    class Meta:
        verbose_name = _("Newsletter")
        verbose_name_plural = _("Newsletters")
        ordering = ["-updated_at"]


class Category(BaseModel):
    """Categories for articles."""

    title = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(unique=True, editable=False)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")
        ordering = ["-updated_at"]


class SavedArticle(BaseModel):
    """Saved Article by user."""

    article = models.JSONField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.user)

    class Meta:
        verbose_name = _("Newsletter")
        verbose_name_plural = _("Newsletters")
        ordering = ["-updated_at"]

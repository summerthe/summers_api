from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext as _

from apps.base.models import BaseModel

User = get_user_model()


class UploadRequest(BaseModel):
    """Represent single upload request made by user.

    To upload one youtube platlist videos to google drive in
    shared folder with service account email.
    """

    START_CHOICE = "START"
    RUNNING_CHOICE = "RUNNING"
    COMPLETED_CHOICE = "COMPLETED"
    FOLDER_NOT_FOUND_CHOICE = "FOLDER_NOT_FOUND_CHOICE"
    PLAYLIST_NOT_FOUND_CHOICE = "PLAYLIST_NOT_FOUND_CHOICE"
    STATUS_CHOICES = (
        (START_CHOICE, START_CHOICE),
        (RUNNING_CHOICE, RUNNING_CHOICE),
        (COMPLETED_CHOICE, COMPLETED_CHOICE),
        (FOLDER_NOT_FOUND_CHOICE, FOLDER_NOT_FOUND_CHOICE),
        (PLAYLIST_NOT_FOUND_CHOICE, PLAYLIST_NOT_FOUND_CHOICE),
    )

    playlist_link = models.URLField()
    playlist_name = models.CharField(max_length=255, blank=True, null=True)

    folder_link = models.URLField()
    status = models.CharField(
        choices=STATUS_CHOICES,
        max_length=25,
        default=START_CHOICE,
        blank=True,
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    slug = models.SlugField(unique=True, editable=False, max_length=400)

    def __str__(self):
        return self.playlist_name

    class Meta:
        verbose_name = _("UploadRequest")
        verbose_name_plural = _("UploadRequests")
        ordering = ["-updated_at"]

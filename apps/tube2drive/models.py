from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext as _

from apps.base.models import BaseModel

User = get_user_model()


class UploadRequest(BaseModel):
    """Represent single upload request made by user.

    To upload one youtube playlist videos to google drive in shared
    folder with service account email.
    """

    NOT_FOUND = "Not Found"
    START_CHOICE = "START"
    RUNNING_CHOICE = "RUNNING"
    COMPLETED_CHOICE = "COMPLETED"
    FOLDER_NOT_FOUND_CHOICE = "FOLDER_NOT_FOUND"
    PLAYLIST_NOT_FOUND_CHOICE = "PLAYLIST_NOT_FOUND"
    VIDEO_NOT_FOUND_CHOICE = "VIDEO_NOT_FOUND"
    CHANNEL_NOT_FOUND_CHOICE = "CHANNEL_NOT_FOUND"
    STATUS_CHOICES = (
        (START_CHOICE, START_CHOICE),
        (RUNNING_CHOICE, RUNNING_CHOICE),
        (COMPLETED_CHOICE, COMPLETED_CHOICE),
        (FOLDER_NOT_FOUND_CHOICE, FOLDER_NOT_FOUND_CHOICE),
        (PLAYLIST_NOT_FOUND_CHOICE, PLAYLIST_NOT_FOUND_CHOICE),
        (VIDEO_NOT_FOUND_CHOICE, VIDEO_NOT_FOUND_CHOICE),
        (CHANNEL_NOT_FOUND_CHOICE, CHANNEL_NOT_FOUND_CHOICE),
    )

    PLAYLIST = "PLAYLIST"
    CHANNEL = "CHANNEL"
    VIDEO = "VIDEO"

    YOUTUBE_ENTITY_CHOICES = (
        (PLAYLIST, PLAYLIST),
        (CHANNEL, CHANNEL),
        (VIDEO, VIDEO),
    )

    youtube_link = models.URLField()
    youtube_entity_name = models.CharField(max_length=255, blank=True, null=True)
    youtube_entity_type = models.CharField(
        choices=YOUTUBE_ENTITY_CHOICES,
        max_length=8,
        default=PLAYLIST,
        blank=True,
    )

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
        return self.youtube_entity_name

    class Meta:
        verbose_name = _("UploadRequest")
        verbose_name_plural = _("UploadRequests")
        ordering = ["-updated_at"]

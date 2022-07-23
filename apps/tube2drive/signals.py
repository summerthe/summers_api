import logging
import multiprocessing
import random
from typing import Type
from urllib.parse import parse_qs, urlparse

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.defaultfilters import slugify

from apps.tube2drive.models import UploadRequest
from apps.tube2drive.services.youtube import Youtube
from apps.tube2drive.utils import find_playlist_and_upload


@receiver(post_save, sender=UploadRequest)
def slugify_upload_request(
    sender: Type[UploadRequest],
    instance: UploadRequest,
    *args,
    **kwargs,
) -> None:
    """Slugify Upload request using the `youtube_entity_name`.

    After the slugify operation, finding youtube video/s and uploading
    will start only if the object was created.

    Parameters
    ----------
    sender : Type[UploadRequest]
    instance : UploadRequest
    """
    if kwargs["created"]:
        # extracting id from link
        try:
            playlist_id = parse_qs(urlparse(instance.youtube_link).query)["list"][0]
        except KeyError:
            playlist_id = None

        youtube_api = Youtube()
        youtube_entity_name = (
            youtube_api.get_playlist_title(playlist_id)
            if playlist_id
            else UploadRequest.NOT_FOUND
        )
        instance.youtube_entity_name = youtube_entity_name

        if instance.youtube_entity_name == UploadRequest.NOT_FOUND:
            instance.status = UploadRequest.PLAYLIST_NOT_FOUND_CHOICE
        instance.slug = slugify(
            instance.youtube_entity_name + str(random.randint(0, 9999)),
        )[:400]

        instance.save()

        # Starting finding and uploading in background
        try:
            main_process = multiprocessing.Process(
                target=find_playlist_and_upload,
                args=(
                    playlist_id,
                    instance.folder_link,
                    instance.pk,
                ),
            )
            main_process.start()
        except Exception as e:
            logging.error(e, exc_info=True)

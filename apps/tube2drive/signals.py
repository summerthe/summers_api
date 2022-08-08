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
from apps.tube2drive.utils import find_videos_and_upload


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
        youtube_entity_type = instance.youtube_entity_type
        youtube_link = instance.youtube_link

        youtube_api = Youtube()
        youtube_entity_id = youtube_entity_name = None
        query_param = ""

        if youtube_entity_type == UploadRequest.VIDEO:
            query_param = "v"
            try:
                youtube_entity_id = parse_qs(urlparse(youtube_link).query)[query_param][
                    0
                ]
            except (KeyError, IndexError):
                pass

            if youtube_entity_id:
                youtube_entity_name = youtube_api.get_video_title(youtube_entity_id)

        elif youtube_entity_type == UploadRequest.PLAYLIST:
            query_param = "list"
            try:
                youtube_entity_id = parse_qs(urlparse(youtube_link).query)[query_param][
                    0
                ]
            except (KeyError, IndexError):
                pass

            if youtube_entity_id:
                youtube_entity_name = youtube_api.get_playlist_title(youtube_entity_id)

        elif youtube_entity_type == UploadRequest.CHANNEL:
            youtube_entity_id = youtube_link.strip("/").split("/")[-1]
            # Dont run channel getting videos, if passed url of playlist.
            if not ("?list=" in youtube_entity_id or "?v=" in youtube_entity_id):
                youtube_entity_name, youtube_entity_id = youtube_api.get_channel_info(
                    youtube_entity_id,
                )

        if not youtube_entity_name:
            youtube_entity_name = UploadRequest.NOT_FOUND
            instance.status = getattr(
                UploadRequest,
                f"{youtube_entity_type}_NOT_FOUND_CHOICE",
            )

        instance.youtube_entity_name = youtube_entity_name

        instance.slug = slugify(
            instance.youtube_entity_name + str(random.randint(0, 9999)),
        )[:400]

        instance.save()

        # Starting finding and uploading in background
        try:
            main_process = multiprocessing.Process(
                target=find_videos_and_upload,
                args=(
                    youtube_entity_id,
                    youtube_entity_type,
                    instance.folder_link,
                    instance.pk,
                ),
            )
            main_process.start()
        except Exception as e:
            logging.error(e, exc_info=True)

import multiprocessing
import random
import traceback
from urllib.parse import parse_qs, urlparse

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.defaultfilters import slugify

from apps.tube2drive.models import UploadRequest
from apps.tube2drive.services.youtube import Youtube
from apps.tube2drive.utils import find_playlist_and_upload


@receiver(post_save, sender=UploadRequest)
def slugify_upload_request(sender, instance, *args, **kwargs):
    if kwargs["created"]:
        # extracting id from link
        try:
            playlist_id = parse_qs(urlparse(instance.playlist_link).query)["list"][0]
        except KeyError:
            playlist_id = None

        youtube_api = Youtube()
        playlist_name = youtube_api.get_playlist_title(playlist_id)
        instance.playlist_name = playlist_name
        instance.slug = slugify(instance.playlist_name + str(random.randint(0, 9999)))[
            :400
        ]
        instance.save()

        # Starting finding and uploading in background
        try:
            main_proces = multiprocessing.Process(
                target=find_playlist_and_upload,
                args=(
                    playlist_id,
                    instance.folder_link,
                    instance.pk,
                ),
            )
            main_proces.start()
        except Exception:
            traceback.print_exc()

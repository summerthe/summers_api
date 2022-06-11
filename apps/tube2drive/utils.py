import json
import os
import time
import traceback

import googleapiclient
import googleapiclient.discovery
import requests
from django.conf import settings
from django.urls import reverse_lazy

from apps.tube2drive.models import UploadRequest
from apps.tube2drive.services.gdrive import Gdrive
from apps.tube2drive.services.youtube import Youtube
from apps.tube2drive.services.youtube_dl import YoutubeDownloader


def find_playlist_and_upload(
    playlist_id: str,
    folder_link: str,
    upload_request_id: int,
) -> None:
    """Find youtube playlist id, download everyvideo and upload to shared gdrive folder.

    Parameters
    ----------
    playlist_id : str
    folder_link : str
    upload_request_id : int
    """
    # hit upload api to update upload request status to running
    update_upload_request_status(upload_request_id, UploadRequest.RUNNING_CHOICE)

    # extracting id from link
    folder_id = folder_link.split("/")[-1]

    youtube_api = Youtube()
    try:
        # fetch all video id from youtube
        videos = youtube_api.fetch_youtube_video_ids(playlist_id)
    except Exception:
        videos = []
        traceback.print_exc()

    if videos is None or len(videos) == 0:
        # if there is no video or playlist is not available set status.
        request_status = UploadRequest.PLAYLIST_NOT_FOUND_CHOICE
    else:

        for counter, video in enumerate(videos, start=1):
            time.sleep(2)
            # get video title from youtube
            video_title = youtube_api.get_video_title(video)

            # make filename with counter as prefix in tmp folder
            filename = "/tmp/{}-{}".format(counter, video_title)
            # `%` is pain for linux file system, so renaming it
            filename = filename.replace("%", "per")

            try:
                youtube_downloader = YoutubeDownloader()
                youtube_downloader.download_video(filename, video)

                # yt_dlp upload file with `.webm` extension
                if not os.path.exists(filename):
                    filename += ".webm"

                try:
                    # upload local file to gdrive
                    gdrive_api = Gdrive()
                    gdrive_api.upload_to_drive(filename, folder_id)
                except googleapiclient.errors.HttpError:
                    traceback.print_exc()
                    request_status = UploadRequest.FOLDER_NOT_FOUND_CHOICE
                    break
                except Exception:
                    traceback.print_exc()
                finally:
                    # remove file regardless it was uploaded or not.
                    os.remove(filename)

            except Exception:
                traceback.print_exc()

        else:
            # if everything went fine set status to completed
            request_status = UploadRequest.COMPLETED_CHOICE

    # hit upload api to update upload request status
    update_upload_request_status(upload_request_id, request_status)


def update_upload_request_status(pk: int, status: str) -> None:
    """Update status of upload request.

    Parameters
    ----------
    pk : int
    status : str
    """
    url = settings.CURRENT_DOMAIN + reverse_lazy(
        "api:apps.tube2drive:upload-requests-detail", kwargs={"pk": pk}
    )
    payload = json.dumps({"status": status})
    headers = {"App-Own": "", "Content-Type": "application/json"}
    requests.request("PUT", url, headers=headers, data=payload)

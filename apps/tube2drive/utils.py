import json
import logging
import os
import time
from threading import Thread

import googleapiclient
import googleapiclient.discovery
from django.conf import settings
from django.urls import reverse_lazy

from apps.common.utils.async_request import AsyncRequest
from apps.tube2drive.models import UploadRequest
from apps.tube2drive.services.google_drive import GoogleDrive
from apps.tube2drive.services.youtube import Youtube
from apps.tube2drive.services.youtube_dl import YoutubeDownloader


def find_videos_and_upload(
    youtube_entity_id: str,
    youtube_entity_type: str,
    folder_link: str,
    upload_request_id: int,
) -> None:
    """Find youtube video/s of youtube_entity_id, download video/s and upload
    it/them to shared google drive folder.

    Parameters
    ----------
    youtube_entity_id : str
    youtube_entity_type : str
    folder_link : str
    upload_request_id : int
    """
    # extracting id from link
    folder_id = folder_link.split("/")[-1]
    google_drive_api = GoogleDrive()

    request_status = UploadRequest.RUNNING_CHOICE
    if not google_drive_api.check_folder_exist(folder_id):
        request_status = UploadRequest.FOLDER_NOT_FOUND_CHOICE
        # if folder is not found or doesnt have permission update status and stop process.
        Thread(
            target=lambda: update_upload_request_status(
                upload_request_id,
                request_status,
            ),
        ).start()
        return

    # hit upload api to update upload request status to running
    update_upload_request_status(upload_request_id, request_status)

    videos = []
    youtube_api = Youtube()
    logger = logging.getLogger("aws")
    if youtube_entity_id:
        try:
            if youtube_entity_type == UploadRequest.VIDEO:
                videos.append(youtube_entity_id)
            elif youtube_entity_type == UploadRequest.PLAYLIST:
                # fetch all video id from youtube playlist
                videos = youtube_api.fetch_playlist_videos_id(youtube_entity_id)
            elif youtube_entity_type == UploadRequest.CHANNEL:
                # fetch latest [500](https://developers.google.com/youtube/v3/docs/search/list#parameters)
                # video id from youtube channel
                videos = youtube_api.fetch_channel_videos_id(youtube_entity_id)
        except Exception as e:
            logger.error(e, exc_info=True)

    try:
        if len(videos) == 0:
            # if there is no video set status.
            request_status = getattr(
                UploadRequest,
                f"{youtube_entity_type}_NOT_FOUND_CHOICE",
            )
        else:
            for counter, video in enumerate(videos, start=1):
                time.sleep(1)
                # get video title from youtube
                video_title = youtube_api.get_video_title(video)

                # if there is no video title, means video was private or deleted.
                if not video_title:
                    continue

                video_title = video_title.replace("/", "-")
                # make filename with counter as prefix in tmp folder
                filename = f"/tmp/{counter}-{video_title}"
                # `%` is pain for linux file system, so renaming it
                filename = filename.replace("%", "per")

                try:
                    youtube_downloader = YoutubeDownloader()
                    did_download = youtube_downloader.download_video(filename, video)
                    if not did_download:
                        continue

                    # yt_dlp upload file with `.webm` extension
                    if not os.path.exists(filename):
                        filename += ".webm"

                    try:
                        # upload local file to google drive
                        google_drive_api.upload_to_drive(filename, folder_id)
                    except googleapiclient.errors.HttpError as e:
                        logger.error(e, exc_info=True)
                        request_status = UploadRequest.FOLDER_NOT_FOUND_CHOICE
                        break
                    except Exception as e:
                        logger.error(e, exc_info=True)
                    finally:
                        # remove file regardless it was uploaded or not.
                        os.remove(filename)

                except Exception as e:
                    logger.error(e, exc_info=True)

            else:
                # if everythng went fine set status to completed
                request_status = UploadRequest.COMPLETED_CHOICE
    except Exception as e:
        logger.error(e, exc_info=True)
    finally:
        # hit upload api to update upload request status
        Thread(
            target=lambda: update_upload_request_status(
                upload_request_id,
                request_status,
            ),
        ).start()


def update_upload_request_status(pk: int, status: str) -> None:
    """Update status of upload request.

    Parameters
    ----------
    pk : int
    status : str
    """
    url = settings.CURRENT_DOMAIN + reverse_lazy(
        "api:apps.tube2drive:upload-requests-detail",
        kwargs={"pk": pk},
    )
    data = json.dumps({"status": status})
    headers = {"App-Own": "", "Content-Type": "application/json"}
    AsyncRequest.run_async(AsyncRequest.put(url, data=data, headers=headers))

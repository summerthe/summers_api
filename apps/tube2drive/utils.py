import json
import logging
import os
import time

import googleapiclient
import googleapiclient.discovery
import requests
from django.conf import settings
from django.urls import reverse_lazy

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
    # hit upload api to update upload request status to running
    request_status = UploadRequest.RUNNING_CHOICE
    update_upload_request_status(upload_request_id, request_status)

    # extracting id from link
    folder_id = folder_link.split("/")[-1]
    videos = []
    youtube_api = Youtube()

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
            logging.error(e, exc_info=True)

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

                # make filename with counter as prefix in tmp folder
                filename = f"/tmp/{counter}-{video_title}"
                # `%` is pain for linux file system, so renaming it
                filename = filename.replace("%", "per")

                try:
                    youtube_downloader = YoutubeDownloader()
                    youtube_downloader.download_video(filename, video)

                    # yt_dlp upload file with `.webm` extension
                    if not os.path.exists(filename):
                        filename += ".webm"

                    try:
                        # upload local file to google drive
                        google_drive_api = GoogleDrive()
                        google_drive_api.upload_to_drive(filename, folder_id)
                    except googleapiclient.errors.HttpError as e:
                        logging.error(e, exc_info=True)
                        request_status = UploadRequest.FOLDER_NOT_FOUND_CHOICE
                        break
                    except Exception as e:
                        logging.error(e, exc_info=True)
                    finally:
                        # remove file regardless it was uploaded or not.
                        os.remove(filename)

                except Exception as e:
                    logging.error(e, exc_info=True)

            else:
                # if everything went fine set status to completed
                request_status = UploadRequest.COMPLETED_CHOICE
    except Exception as e:
        logging.error(e, exc_info=True)
    finally:
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
        "api:apps.tube2drive:upload-requests-detail",
        kwargs={"pk": pk},
    )
    payload = json.dumps({"status": status})
    headers = {"App-Own": "", "Content-Type": "application/json"}
    requests.request("PUT", url, headers=headers, data=payload)

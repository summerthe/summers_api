import json
import logging
import os
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
from apps.tube2drive.websocket import broadcast_upload_request_update
from summers_api.celery import app as celery_app


def find_videos_and_upload(
    youtube_entity_id: str,
    youtube_entity_type: str,
    folder_link: str,
    upload_request_id: int,
    user_uuid: str,
) -> None:
    """Find youtube video/s of youtube_entity_id, download video/s and upload
    it/them to shared google drive folder.

    Parameters
    ----------
    youtube_entity_id : str
    youtube_entity_type : str
    folder_link : str
    upload_request_id : int
    user_uuid : str
    """
    # extracting id from link
    folder_id = folder_link.split("/")[-1]
    google_drive_api = GoogleDrive()

    request_status = UploadRequest.RUNNING_CHOICE
    if not google_drive_api.check_folder_exist(folder_id):
        request_status = UploadRequest.FOLDER_NOT_FOUND_CHOICE
        # if folder is not found or doesnt have permission update status and stop process.
        update_upload_request_status(
            upload_request_id,
            request_status,
            user_uuid,
        )
        return

    # hit upload api to update upload request status to running
    update_upload_request_status(
        upload_request_id,
        request_status,
        user_uuid,
    )

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
                # fetch latest [500 videos](https://developers.google.com/youtube/v3/docs/search/list#parameters)
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
            # hit upload api to update upload request status
            update_upload_request_status(
                upload_request_id,
                request_status,
                user_uuid,
            )
        else:
            from apps.tube2drive.tasks import task_download_upload_single
            for counter, video in enumerate(videos, start=1):
                if settings.USE_REDIS:
                    celery_app.send_task(
                        "apps.tube2drive.tasks.task_download_upload_single",
                        args=(
                            video,
                            upload_request_id,
                            request_status,
                            folder_id,
                            counter,
                            counter == len(videos),
                            user_uuid,
                        ),
                        queue="tube2drive_queue",
                    )
                else:
                    th = Thread(target=task_download_upload_single, args=(video,
                        upload_request_id,
                        request_status,
                        folder_id,
                        counter,
                        counter == len(videos),
                        user_uuid,
                    ))
                    th.start()
                    th.join()
    except Exception as e:
        logger.error(e, exc_info=True)


def download_upload_single(
    video: str,
    upload_request_id: str,
    request_status: str,
    folder_id: str,
    counter: int,
    is_last: bool,
    user_uuid: str,
) -> str:
    """Download and upload one single video from youtube to drive.

    Parameters
    ----------
    video : str
    upload_request_id : str
    request_status : str
    folder_id : str
    counter : int
    is_last : bool
    user_uuid : str

    Returns
    -------
    str
    """
    # get video title from youtube
    youtube_api = Youtube()
    logger = logging.getLogger("aws")
    video_title = youtube_api.get_video_title(video)
    if is_last:
        request_status = UploadRequest.COMPLETED_CHOICE
    try:
        # if there is no video title, means video was private or deleted.
        if not video_title:
            return request_status

        video_title = video_title.replace("/", "-")
        # make filename with counter as prefix in tmp folder
        filename = f"/tmp/{counter}-{video_title}"
        # `%` is pain for linux file system, so renaming it
        filename = filename.replace("%", "per")
        youtube_downloader = YoutubeDownloader()
        did_download = youtube_downloader.download_video(
            filename,
            video,
            counter,
        )
        if not did_download:
            return request_status

        # yt_dlp upload file with `.webm` extension
        if not os.path.exists(filename):
            filename += ".webm"

        google_drive_api = GoogleDrive()
        try:
            # upload local file to google drive
            google_drive_api.upload_to_drive(filename, folder_id)
        except googleapiclient.errors.HttpError as e:
            logger.error(e, exc_info=True)
            request_status = UploadRequest.FOLDER_NOT_FOUND_CHOICE
        except Exception as e:
            logger.error(e, exc_info=True)
        finally:
            # remove file regardless it was uploaded or not.
            os.remove(filename)

    except Exception as e:
        logger.error(e, exc_info=True)

    finally:
        if is_last:
            update_upload_request_status(
                upload_request_id,
                request_status,
                user_uuid,
            )

    return request_status


def update_upload_request_status(
    pk: int,
    status: str,
    user_uuid: str,
) -> None:
    """Update status of upload request.

    Parameters
    ----------
    pk : int
    status : str
    user_uuid : str
    """
    url = settings.CURRENT_DOMAIN + reverse_lazy(
        "api:apps.tube2drive:upload-requests-detail",
        kwargs={"pk": pk},
    )
    data = json.dumps({"status": status})
    headers = {"App-Own": "", "Content-Type": "application/json"}
    response = AsyncRequest.run_async(AsyncRequest.put(url, data=data, headers=headers))

    text_respone = json.dumps(response)
    try:
        # TODO: This returns 500 in local
        AsyncRequest.run_async(broadcast_upload_request_update(user_uuid, text_respone))
    except Exception:
        pass
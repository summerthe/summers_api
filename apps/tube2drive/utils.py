import json
import os
import time
import traceback
from typing import List

import googleapiclient
import googleapiclient.discovery
import psutil
import requests
import yt_dlp
from django.conf import settings
from django.urls import reverse_lazy
from google.oauth2 import service_account
from googleapiclient.http import MediaFileUpload

from apps.tube2drive.models import UploadRequest


def find_playlist_and_upload(
    playlist_id: str,
    folder_id: str,
    upload_request_id: int,
) -> None:
    """Find youtube playlist id, download everyvideo and upload to shared gdrive folder.

    Parameters
    ----------
    playlist_id : str
    folder_id : str
    upload_request_id : int
    """
    # hit upload api to update upload request status to running
    update_upload_request_status(upload_request_id, UploadRequest.RUNNING_CHOICE)

    try:
        # fetch all video id from youtube
        videos = fetch_youtube_video_ids(playlist_id)
    except Exception:
        videos = []
        traceback.print_exc()

    if videos is None or len(videos) == 0:
        # if there is no videos
        request_status = UploadRequest.PLAYLIST_NOT_FOUND_CHOICE
    else:
        scopes = ["https://www.googleapis.com/auth/youtube.readonly"]
        youtube_api_service_name = "youtube"
        youtube_api_version = "v3"
        credentials = service_account.Credentials.from_service_account_info(
            settings.GCP_SERVICE_ACCOUNT_JSON,
            scopes=scopes,
        )
        youtube_client = googleapiclient.discovery.build(
            youtube_api_service_name,
            youtube_api_version,
            credentials=credentials,
            cache_discovery=False,
        )
        counter = 1
        for video in videos:
            time.sleep(2)
            # get youtube video details
            request = youtube_client.videos().list(part="snippet", id=video)
            response = request.execute()

            filename = "/tmp/{}-{}".format(
                counter, response["items"][0]["snippet"]["title"]
            )
            filename = filename.replace("%", "per")
            try:
                while (
                    psutil.Process(os.getpid()).memory_info().rss
                    < 320 * 1024 * 1024  # 320MB
                ):
                    time.sleep(2)
                download_video()

                if not os.path.exists(filename):
                    # adding webm extension on filename when yt_dlp don't add
                    filename += ".webm"

                while (
                    psutil.Process(os.getpid()).memory_info().rss
                    < 320 * 1024 * 1024  # 320MB
                ):
                    time.sleep(2)

                try:
                    # upload local file to gdrive
                    upload_to_drive(filename, folder_id)
                except googleapiclient.errors.HttpError:
                    request_status = UploadRequest.FOLDER_NOT_FOUND_CHOICE
                    break
                except Exception:
                    traceback.print_exc()
                finally:
                    # finally always run even on break
                    os.remove(filename)
            except Exception:
                traceback.print_exc()
            counter += 1
        else:
            # if everything went fine set status to completed
            request_status = UploadRequest.COMPLETED_CHOICE

    # hit upload api to update upload request status
    update_upload_request_status(upload_request_id, request_status)


def download_video(filename, video):
    ydl_opts = {"outtmpl": filename}
    # checks whether approx filesize of default format is greater than limit or not,
    # if file size is greather than find a format which has lesser size than
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(
                "https://www.youtube.com/watch?v={}".format(video),
                download=False,
            )
            filesize_approx = info.get("filesize_approx")  # in bytes
            MAX_FILE_SIZE = 150 * 1024 * 1024  # 150Mb
            if filesize_approx > MAX_FILE_SIZE:
                # sort formats by filesize desc
                formats = sorted(
                    info.get("formats"),
                    key=lambda format: int(format.get("filesize"))
                    if format.get("filesize")
                    else 0,
                    reverse=True,
                )
                format_to_use = None
                # find format which is less than max limit.
                for format in formats:
                    try:
                        print("Current size", int(format.get("filesize")))
                        if (
                            int(format.get("filesize")) < MAX_FILE_SIZE
                            and format.get("vcodec") != "none"
                            and format.get("acodec") != "none"
                        ):
                            format_to_use = format.get("format_id")
                            break
                    except Exception:
                        pass
                ydl_opts["format"] = format_to_use

                if not format_to_use:
                    return

        except Exception:
            pass

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.download(
                ["https://www.youtube.com/watch?v={}".format(video)],
            )
        except Exception:
            pass


def fetch_youtube_video_ids(playlist_id: str) -> List[str]:
    """Hit youtube playlist api to get list of videos id of playlist.

    Parameters
    ----------
    playlist_id : str

    Returns
    -------
    List[str]
        List of videos id
    """
    scopes = ["https://www.googleapis.com/auth/youtube.readonly"]
    youtube_api_service_name = "youtube"
    youtube_api_version = "v3"
    credentials = service_account.Credentials.from_service_account_info(
        settings.GCP_SERVICE_ACCOUNT_JSON,
        scopes=scopes,
    )
    youtube_client = googleapiclient.discovery.build(
        youtube_api_service_name,
        youtube_api_version,
        credentials=credentials,
        cache_discovery=False,
    )
    responses = []
    request = youtube_client.playlistItems().list(
        part="snippet",
        playlistId=playlist_id,
    )
    response = request.execute()
    responses.append(response)
    # All videos id
    video_ids = []

    # for first page
    try:
        for item in response["items"]:
            video_ids.append(item["snippet"]["resourceId"]["videoId"])
    except Exception:
        traceback.print_exc()

    # iterating over pagination and fetching all video_ids
    try:
        while True:
            try:
                request = youtube_client.playlistItems().list(
                    part="snippet",
                    playlistId=playlist_id,
                    pageToken=response["nextPageToken"],
                )
            except KeyError:
                # if there is no nextPageToken means we have already fetched last page
                # and there is no more videos to fetch.
                break
            response = request.execute()
            for item in response["items"]:
                try:
                    # only extracting video id
                    video_ids.append(item["snippet"]["resourceId"]["videoId"])
                except Exception:
                    traceback.print_exc()
    except Exception:
        traceback.print_exc()
    return video_ids


def upload_to_drive(
    filename: str,
    folder_id: str,
) -> None:
    """Upload local file to google drive in passed folder_id.

    Parameters
    ----------
    filename : str
    folder_id : str
    """
    # Call the Drive v3 API
    # create folder in your account and share that folder with service account,
    # so service account can create file in that folder.
    scopes = ["https://www.googleapis.com/auth/drive"]
    drive_api_service_name = "drive"
    drive_api_version = "v3"
    credentials = service_account.Credentials.from_service_account_info(
        settings.GCP_SERVICE_ACCOUNT_JSON,
        scopes=scopes,
    )
    drive_client = googleapiclient.discovery.build(
        drive_api_service_name,
        drive_api_version,
        credentials=credentials,
        cache_discovery=False,
    )
    file_metadata = {"name": filename.lstrip("/tmp/"), "parents": [folder_id]}
    media = MediaFileUpload(filename, mimetype="video/*")
    # uploading
    drive_client.files().create(
        body=file_metadata, media_body=media, fields="id"
    ).execute()


def update_upload_request_status(pk: int, status: str) -> None:
    """Updata status of upload request.

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

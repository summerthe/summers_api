import logging
import os
import shutil
import uuid

import requests
import yt_dlp
from django.conf import settings


class YoutubeDownloader:
    """Uses youtube_dl to get youtube file data and download it."""

    def download_video(self, filename: str, video_id: str, counter: int = 1) -> bool:
        """Download youtube video using youtube_dl and save as `filename`.

        Parameters
        ----------
        filename : str
        video_id : str
        """
        logger = logging.getLogger("aws")

        tmp_filename = f"/tmp/{uuid.uuid4()}.webm"
        ydl_opts = {"outtmpl": tmp_filename}

        if settings.DOWNLOAD_BEST_QUALITY and settings.STORE_TUBE2DRIVE_LOCAL:
            ydl_opts["format"] = "bestvideo[ext=mp4]+bestaudio[ext=mp4]/best[ext=mp4]"

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                youtube_video_url = f"https://www.youtube.com/watch?v={video_id}"
                if settings.DOWNLOAD_BEST_QUALITY and settings.STORE_TUBE2DRIVE_LOCAL:
                    ydl.download([youtube_video_url])
                    return True

                info = ydl.extract_info(
                    youtube_video_url,
                    download=False,
                )
                formats = sorted(
                    info.get("formats"),
                    key=lambda format: int(format.get("resolution").split("x")[0])
                    if format.get("resolution").split("x")[0].isnumeric()
                    else 0,
                    reverse=True,
                )
                for format in formats:
                    if (
                        format.get("vcodec") != "none"
                        and format.get("acodec") != "none"
                    ):
                        url_to_download = format.get("url")
                        # not downloading video if size is greater than set limit in MB.
                        # filesize_approx is in bytes
                        # not ristricting for local download
                        if (
                            not settings.STORE_TUBE2DRIVE_LOCAL
                            and format.get("filesize_approx", 0)
                            > settings.YOUTUBE_DL_FILE_LIMIT * 1024 * 1024
                        ):
                            logger.info(
                                f"""Skipping {counter} video: `{video_id}` due to oversize,
                                filesize_approx: {format.get('filesize_approx')}(bytes)""",
                            )
                            return False
                        with requests.get(url_to_download, stream=True) as r:
                            with open(tmp_filename, "wb") as f:
                                shutil.copyfileobj(r.raw, f)

                        os.rename(tmp_filename,filename)
                        return True
            except Exception as e:
                logger.error(e, exc_info=True)
                try:
                    os.remove(tmp_filename)
                except:
                    pass

        return False

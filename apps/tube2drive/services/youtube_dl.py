import logging
import shutil

import requests
import yt_dlp
from django.conf import settings


class YoutubeDownloader:
    """Uses youtube_dl to get youtube file data and download it."""

    def download_video(self, filename: str, video_id: str) -> bool:
        """Download youtube video using youtube_dl and save as `filename`.

        Parameters
        ----------
        filename : str
        video_id : str
        """
        logger = logging.getLogger("aws")

        ydl_opts = {"outtmpl": filename}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(
                    f"https://www.youtube.com/watch?v={video_id}",
                    download=False,
                )
                # not downloading video if size is greater than set limit in MB.
                # filesize_approx is in bytes
                if (
                    info.get("filesize_approx", 0)
                    > settings.YOUTUBE_DL_FILE_LIMIT * 1024 * 1024
                ):
                    logger.info(
                        f"Skipping video `{video_id}` due to oversize {info.get('filesize_approx')}(bytes)",
                    )
                    return False
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
                        with requests.get(url_to_download, stream=True) as r:
                            with open(filename, "wb") as f:
                                shutil.copyfileobj(r.raw, f)
                        return True
            except Exception as e:
                logger.error(e, exc_info=True)
        return False

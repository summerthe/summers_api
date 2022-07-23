import shutil

import requests
import yt_dlp


class YoutubeDownloader:
    """Uses youtube_dl to get youtube file data and download it."""

    def download_video(self, filename: str, video_id: str) -> None:
        """Download youtube video using youtube_dl and save as `filename`.

        Parameters
        ----------
        filename : str
        video_id : str
        """
        ydl_opts = {"outtmpl": filename}
        # checks whether approx filesize of default format is greater than limit or not,
        # if file size is greater than find a format which has lesser size than
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(
                    f"https://www.youtube.com/watch?v={video_id}",
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
                        with requests.get(url_to_download, stream=True) as r:
                            with open(filename, "wb") as f:
                                shutil.copyfileobj(r.raw, f)
                        break
            except Exception:
                pass

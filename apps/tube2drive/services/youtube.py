import logging

import googleapiclient
import googleapiclient.discovery
from django.conf import settings
from google.oauth2 import service_account

from apps.tube2drive.models import UploadRequest


class Youtube:
    """Youtube module is to interact with Youtube Data API.

    For more details checkout the [API Reference](https://developers.google.com/youtube/v3/docs).
    """

    def __init__(self) -> None:
        """Initialize clients."""
        scopes = ["https://www.googleapis.com/auth/youtube.readonly"]
        youtube_api_service_name = "youtube"
        youtube_api_version = "v3"
        credentials = service_account.Credentials.from_service_account_info(
            settings.GCP_SERVICE_ACCOUNT_JSON,
            scopes=scopes,
        )
        self.youtube_client = googleapiclient.discovery.build(
            youtube_api_service_name,
            youtube_api_version,
            credentials=credentials,
            cache_discovery=False,
        )

    def fetch_playlist_videos_id(self, playlist_id: str) -> list[str]:
        """Hit youtube playlist api to get list of videos id of playlist.

        Parameters
        ----------
        playlist_id : str

        Returns
        -------
        list[str]
            List of videos id of playlist.
        """
        # All videos id
        videos_id = []
        next_page_token = None
        # iterating over pagination and fetching all videos_id
        try:
            while True:
                request = self.youtube_client.playlistItems().list(
                    part="snippet",
                    playlistId=playlist_id,
                    pageToken=next_page_token,
                    maxResults=50,
                )
                response = request.execute()
                for item in response["items"]:
                    try:
                        # only extracting video id
                        videos_id.append(item["snippet"]["resourceId"]["videoId"])
                    except Exception as e:
                        logging.error(e, exc_info=True)

                # If next page token is empty after fetching the results,
                # means there is no more data to fetch from API.
                next_page_token = response.get("nextPageToken")
                if next_page_token is None:
                    break
        except Exception as e:
            logging.error(e, exc_info=True)
        return videos_id

    def fetch_channel_videos_id(self, channel_id: str) -> list[str]:
        """Hit youtube search api to get list of top 500 videos id of channel.

        Parameters
        ----------
        channel_id : str

        Returns
        -------
        list[str]
            List of videos id of channel.
        """
        # All videos id
        videos_id = []
        next_page_token = None
        # iterating over pagination and fetching all videos_id
        try:
            while True:
                request = self.youtube_client.search().list(
                    part="snippet",
                    channelId=channel_id,
                    order="date",
                    type="video",
                    pageToken=next_page_token,
                    maxResults=50,
                )
                response = request.execute()
                for item in response["items"]:
                    try:
                        # only extracting video id
                        videos_id.append(item["id"]["videoId"])
                    except Exception as e:
                        logging.error(e, exc_info=True)

                # If next page token is empty after fetching the results,
                # means there is no more data to fetch from API.
                next_page_token = response.get("nextPageToken")
                if next_page_token is None:
                    break
        except Exception as e:
            logging.error(e, exc_info=True)
        return videos_id

    def get_video_title(self, video_id: str) -> str | None:
        """Fetch video title using youtube api from video id.

        Parameters
        ----------
        video_id : str

        Returns
        -------
        str | None
        """
        request = self.youtube_client.videos().list(part="snippet", id=video_id)
        response = request.execute()
        if len(response["items"]) > 0:
            title = response["items"][0]["snippet"]["title"]
            return title
        return None

    def get_playlist_title(self, playlist_id: str) -> str:
        """Fetch playlist title using youtube api from playlist id.

        Parameters
        ----------
        playlist : str

        Returns
        -------
        str
        """
        try:
            request = self.youtube_client.playlists().list(
                part="snippet",
                id=playlist_id,
            )
            response = request.execute()
            title = response["items"][0]["snippet"]["title"]
            return title
        except Exception:
            return UploadRequest.NOT_FOUND

    def get_channel_info(self, channel_query: str) -> tuple[str | None, str | None]:
        request = self.youtube_client.search().list(
            part="snippet",
            channelType="any",
            q=channel_query,
            type="channel",
        )
        response = request.execute()
        channel_id: str | None = None
        channel_title: str | None = None

        try:
            channel_snippet = response["items"][0]["snippet"]
            channel_id = channel_snippet["channelId"]
            channel_title = channel_snippet["title"]
        except (KeyError, IndexError):
            pass
        return channel_title, channel_id

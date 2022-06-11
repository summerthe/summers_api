import traceback
from typing import List

import googleapiclient
import googleapiclient.discovery
from django.conf import settings
from google.oauth2 import service_account


class Youtube:
    def __init__(self) -> None:
        """Initalize clients."""
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

    def fetch_youtube_video_ids(self, playlist_id: str) -> List[str]:
        """Hit youtube playlist api to get list of videos id of playlist.

        Parameters
        ----------
        playlist_id : str

        Returns
        -------
        List[str]
            List of videos id
        """
        responses = []
        request = self.youtube_client.playlistItems().list(
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
                    request = self.youtube_client.playlistItems().list(
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

    def get_video_title(self, video_id: str) -> str:
        """Fetch video title using youtube api from video id.

        Parameters
        ----------
        video_id : str

        Returns
        -------
        str
        """
        request = self.youtube_client.videos().list(part="snippet", id=video_id)
        response = request.execute()
        title = response["items"][0]["snippet"]["title"]
        return title

    def get_playlist_title(self, playlist_id: str) -> str:
        """Fetch playlist title using youtube api from playlist id.

        Parameters
        ----------
        playlist : str

        Returns
        -------
        str
        """
        request = self.youtube_client.playlists().list(part="snippet", id=playlist_id)
        response = request.execute()
        try:
            title = response["items"][0]["snippet"]["title"]
            return title
        except Exception:
            return "Not Found"

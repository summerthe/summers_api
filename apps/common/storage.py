import json
from typing import IO, Any

import requests
from django.conf import settings
from django.core.files import File
from django.core.files.storage import Storage


class CustomFileStorage(Storage):
    """Custom file storage to upload different content type on different
    storage platforms."""

    def _open(self, name: str, mode: str = "rb") -> None:
        return None

    def _save(self, name: str | None, content: IO[Any]) -> str:
        """Upload file to 3rd party storage.

        Currently Imgur supported image and videos format are getting upload to Imgur.

        Parameters
        ----------
        name : str | None
        content : IO[Any]

        Returns
        -------
        str
        """
        content_type = (
            content.content_type if hasattr(content, "content_type") else None  # type: ignore[attr-defined]
        )
        if content_type in settings.IMGUR_SUPPORTED_FORMAT:
            file_url = self.upload_to_imgur(content)
            if file_url:
                return file_url
        # TODO(summer): upload somewhere else
        return "somewhere"

    def exists(self, name: str) -> bool:
        return False

    def url(self, name: str | None) -> str | None:  # type: ignore[override]
        return name

    def upload_to_imgur(self, thumbnail: IO[Any]) -> str | None:
        """Upload supported imgur files to imgur storage using API.

        Parameters
        ----------
        thumbnail : IO[Any]


        Returns
        -------
        str | None
        """
        file_in_bytes = File(thumbnail).read()
        data = {"image": file_in_bytes}
        headers = {"Authorization": f"Client-ID {settings.IMGUR_CLIENT_ID}"}
        response = requests.post(
            settings.IMGUR_UPLOAD_ENDPOINT,
            data=data,
            headers=headers,
        )
        if response.status_code == 200:
            return json.loads(response.content.decode()).get("data").get("link")
        return None

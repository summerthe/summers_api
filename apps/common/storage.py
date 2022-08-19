from typing import IO, Any

from django.conf import settings
from django.core.files import File
from django.core.files.storage import Storage

from apps.common.services.amazon_s3 import AmazonS3
from apps.common.services.imgur import Imgur


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
        # try to upload imgur if the content type is supported by imgur,
        # otherwise upload to aws s3
        if content_type in settings.IMGUR_SUPPORTED_FORMAT:
            file_in_bytes = File(content).read()
            file_url = Imgur().upload(file_in_bytes)
            if file_url:
                return file_url

        file_url = AmazonS3().upload(file_in_bytes, name)
        return file_url

    def exists(self, name: str) -> bool:
        return False

    def url(self, name: str | None) -> str | None:  # type: ignore[override]
        return name

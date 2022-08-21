import logging

from django.conf import settings

from apps.common.utils.async_request import AsyncRequest


class Imgur:
    def upload(self, file_in_bytes: bytes) -> str | None:
        """Upload supported imgur files to imgur storage using API.

        Parameters
        ----------
        file : bytes

        Returns
        -------
        str | None
        """
        data = {"image": file_in_bytes}
        headers = {"Authorization": f"Client-ID {settings.IMGUR_CLIENT_ID}"}

        response = AsyncRequest.run_async(
            AsyncRequest.post(
                settings.IMGUR_UPLOAD_ENDPOINT,
                data=data,
                headers=headers,
            ),
        )

        if response:
            return response["data"]["link"]
        logger = logging.getLogger("aws")
        logger.error(
            f"Imgur : file upload failed \nResponse:{response}\nFile: {file_in_bytes}",
        )
        return None

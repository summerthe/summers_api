import json

import requests
from django.conf import settings
from django.core.files import File
from django.core.files.storage import Storage


class CustomFileStorage(Storage):
    def _open(self, name, mode="rb"):
        return None

    def _save(self, name, content):
        content_type = content.content_type
        if content_type in settings.IMGUR_SUPPORTED_FORMAT:
            file_url = self.upload_to_imgur(content)
            if file_url:
                return file_url
        # TODO(summer): upload somewhere else

    def exists(self, name):
        return False

    def url(self, name):
        return name

    def upload_to_imgur(self, thumbnail):
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

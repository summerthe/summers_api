import googleapiclient
import googleapiclient.discovery
from django.conf import settings
from google.oauth2 import service_account
from googleapiclient.http import MediaFileUpload


class Gdrive:
    def __init__(self) -> None:
        """Initalize clients."""
        scopes = ["https://www.googleapis.com/auth/drive"]
        drive_api_service_name = "drive"
        drive_api_version = "v3"
        credentials = service_account.Credentials.from_service_account_info(
            settings.GCP_SERVICE_ACCOUNT_JSON,
            scopes=scopes,
        )
        self.drive_client = googleapiclient.discovery.build(
            drive_api_service_name,
            drive_api_version,
            credentials=credentials,
            cache_discovery=False,
        )

    def upload_to_drive(
        self,
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
        # create folder in user's gdrive account and share that folder with service account,
        # so service account can create file in that folder.
        file_metadata = {"name": filename.lstrip("/tmp/"), "parents": [folder_id]}
        media = MediaFileUpload(filename, mimetype="video/*")
        # uploading
        self.drive_client.files().create(
            body=file_metadata,
            media_body=media,
            fields="id",
        ).execute()

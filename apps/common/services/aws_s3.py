import logging

import boto3
from django.conf import settings


class AWS_S3:
    def __init__(self) -> None:
        session = boto3.Session(
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )
        self.client = session.resource("s3")
        self.bucket = settings.AWS_S3_BUCKET
        self.object_url_prefix = settings.AWS_S3_ORIGIN

    def upload(self, file_in_bytes: bytes, filename: str) -> str:
        """Upload files to s3 bucket.

        Parameters
        ----------
        file_in_bytes : bytes
        filename : str

        Returns
        -------
        str
        """
        try:
            s3_object = self.client.Object(self.bucket, filename)
            s3_object.put(Body=file_in_bytes)
            url = f"{self.object_url_prefix}/{filename}"
            return url
        except Exception as e:
            logger = logging.getLogger("aws")
            logger.error(e, exc_info=True)
            logger.error(
                f"AWS S3 : file upload failed \nException:{e}\nFile: {file_in_bytes}\nFilename: {filename}",
            )

        return None

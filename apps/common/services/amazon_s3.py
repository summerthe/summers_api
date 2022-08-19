import boto3
from django.conf import settings


class AmazonS3:
    def __init__(self) -> None:
        session = boto3.Session(
            aws_access_key_id=settings.A_S3_ACCESS_KEY_ID,
            aws_secret_access_key=settings.A_S3_SECRET_ACCESS_KEY,
        )
        self.client = session.resource("s3")
        self.bucket = settings.A_S3_BUCKET

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

        s3_object = self.client.Object(self.bucket, filename)
        s3_object.put(Body=file_in_bytes, ACL="public-read")
        url = f"https://{self.bucket}.s3.amazonaws.com/{filename}"
        return url

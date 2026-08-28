import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from botocore.config import Config

# util imports
import logging
import os
from ..settings import get_settings

CONFIG = get_settings()

logger = logging.getLogger(__name__)
logger.setLevel(CONFIG.log_level)
file_handler = logging.FileHandler(filename=CONFIG.logs_file)
file_handler.setLevel(CONFIG.log_level)
file_handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"))
logger.addHandler(file_handler)

class BlobStore:
    def __init__(
        self, 
        bucket_name: str, 
        endpoint_url: str | None = None, 
        region_name: str = "ap-south-2"
    ):
        """
        Initializes the S3 Client.
        """
        self.bucket_name = bucket_name
        
        # Production config: standard retry mode and timeouts
        client_config = Config(
            retries={"max_attempts": 3, "mode": "standard"},
            connect_timeout=5,
            read_timeout=15,
            max_pool_connections=50
        )

        self.s3_client = boto3.client( # pyright: ignore
            's3',
            endpoint_url=endpoint_url,
            region_name=region_name,
            aws_access_key_id=CONFIG.aws_access_token,
            aws_secret_access_key=CONFIG.aws_secret_key,
            config=client_config
        )

    def list_objects(self):
        try:
            return self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Delimiter=","
            )
        except NoCredentialsError:
            logger.error("Permission denied to list objects")


    def upload_file(self, file_path: str, object_name: str | None = None) -> bool:
        """Uploads a file to the S3 bucket."""
        if object_name is None:
            object_name = os.path.basename(file_path)

        try:
            self.s3_client.upload_file(file_path, self.bucket_name, object_name)
            logger.info(f"Successfully uploaded {file_path} to {self.bucket_name}/{object_name}")
            return True
        except NoCredentialsError as e:
            logger.error("Permission denied to upload {}: {}".format(file_path, e))
            return False
        except ClientError as e:
            logger.error("Failed to upload {}: {}".format(file_path, e))
            return False
        except FileNotFoundError:
            logger.error("The file was not found: {}".format(file_path))
            return False

    def download_file(self, object_name: str, file_path: str) -> bool:
        """Downloads a file from the S3 bucket."""
        try:
            self.s3_client.download_file(self.bucket_name, object_name, file_path)
            logger.info("Successfully downloaded {} to {}".format(object_name, file_path))
            return True
        except ClientError as e:
            logger.error("Failed to download {}: {}".format(object_name, e))
            return False

    def generate_presigned_url(self, object_name: str, expiration: int = 3600):
        """Generates a presigned URL to share an S3 object securely."""
        try:
            response = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': object_name},
                ExpiresIn=expiration
            )
            return response
        except ClientError as e:
            logger.error("Failed to generate presigned URL for {}: {}".format(object_name, e))
            return None
        
    def generate_presigned_upload(self, object_name: str, file_type: str = "image/jpeg", expiration: int = 3600):
        """
        Generates a presigned POST dictionary so the frontend can upload directly to S3.
        """
        try:
            response = self.s3_client.generate_presigned_post(
                Bucket=self.bucket_name,
                Key=object_name,
                Fields={'Content-Type': file_type},
                Conditions=[
                    {'Content-Type': file_type},
                    ['content-length-range', 1, 10485760] # Restrict size (e.g., max 10MB)
                ],
                ExpiresIn=expiration
            )
            return response # Returns a dict with 'url' and 'fields' for the frontend
        except ClientError as e:
            logger.error("Failed to generate presigned POST for {}: {}".format(object_name, e))
            return None
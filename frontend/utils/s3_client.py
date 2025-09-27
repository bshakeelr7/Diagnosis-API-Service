import boto3
import os

class S3Client:
    def __init__(self):
        self.s3 = boto3.client(
            "s3",
            endpoint_url="http://localhost:9000",  # MinIO endpoint
            aws_access_key_id="admin",
            aws_secret_access_key="admin123",
            region_name="us-east-1"
        )
        self.bucket_name = "uploads"
        self._ensure_bucket()

    def _ensure_bucket(self):
        try:
            self.s3.create_bucket(Bucket=self.bucket_name)
        except self.s3.exceptions.BucketAlreadyOwnedByYou:
            pass

    def upload_file(self, file_bytes: bytes, filename: str):
        self.s3.put_object(Bucket=self.bucket_name, Key=filename, Body=file_bytes)
        return f"s3://{self.bucket_name}/{filename}"

    def download_file(self, filename: str, local_dir="images"):
        os.makedirs(local_dir, exist_ok=True)
        local_path = os.path.join(local_dir, filename)
        self.s3.download_file(self.bucket_name, filename, local_path)
        return local_path


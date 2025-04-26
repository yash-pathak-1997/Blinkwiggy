import boto3
import os
from botocore.client import Config

MINIO_ENDPOINT = "http://host.docker.internal:9000"
ACCESS_KEY = "minioadmin"
SECRET_KEY = "minioadmin123"
BUCKET_NAME = "user-image-dev"


def upload_to_minio_task(file_path, username):
    # Init MinIO client
    s3 = boto3.client(
        's3',
        endpoint_url=MINIO_ENDPOINT,
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
        config=Config(signature_version='s3v4'),
        region_name='us-east-1'
    )

    # Ensure bucket exists
    try:
        s3.head_bucket(Bucket=BUCKET_NAME)
    except Exception as e:
        print(str(e))
        s3.create_bucket(Bucket=BUCKET_NAME)

    filename = os.path.basename(file_path)
    s3.upload_file(file_path, BUCKET_NAME, f"{username}/{filename}")
    print(f"[UPLOAD] {file_path} uploaded to {BUCKET_NAME}/{username}/{filename}")

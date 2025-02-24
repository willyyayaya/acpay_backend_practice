import os
from tempfile import NamedTemporaryFile
from typing import List

import boto3
from botocore.config import Config
from fastapi import UploadFile

from src.schemas.basic import UploadedFile

s3 = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_REGION'),
    config=Config(s3={"use_accelerate_endpoint": False})
)


def upload_local_to_s3(local_path, s3_path, content_type):
    s3.upload_file(local_path, str(os.environ.get('AWS_S3_BUCKET')), s3_path, ExtraArgs={'ContentType': content_type})
    public_url = f"https://{os.getenv('AWS_S3_BUCKET')}.s3.{os.getenv('AWS_REGION')}.amazonaws.com/{s3_path}"
    return public_url


def save_upload_files_locally(files: List[UploadFile] | UploadFile) -> List[UploadedFile]:
    entries = []

    for file in files:
        file_extension = file.filename.split(".")[-1]

        with NamedTemporaryFile(delete=False, suffix=f".{file_extension}") as temp_file:
            file_content = file.file.read()
            temp_file.write(file_content)
            temp_file.flush()

        entries.append(
            UploadedFile(
                path=temp_file.name,
                original_file_name=file.filename,
                extension=file_extension,
                content_type=file.content_type
            )
        )

    return entries

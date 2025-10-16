from fastapi import UploadFile
from minio import Minio

import settings


def upload_attachment(
    client: Minio, document_id: str, attachment_id: str, file: UploadFile
):
    object_name = f"{document_id}/{attachment_id}"
    client.put_object(
        bucket_name=settings.MINIO_BUCKET,
        object_name=object_name,
        data=file.file,
        length=file.size,
        content_type=file.content_type,
    )

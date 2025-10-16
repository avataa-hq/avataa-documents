from minio import Minio

import settings


def remove_object_latest_version(
    document_id: str, attachment_id: str, client: Minio
):
    attachment_name = f"{document_id}/{attachment_id}"
    versions = client.list_objects(
        settings.MINIO_BUCKET, attachment_name, include_version=True
    )
    latest_file_version = None
    for v in versions:
        if not v.is_latest:
            continue
        if v.is_delete_marker:
            break
        latest_file_version = v.version_id
        break

    if latest_file_version:
        client.remove_object(
            bucket_name=settings.MINIO_BUCKET,
            object_name=attachment_name,
            version_id=latest_file_version,
        )

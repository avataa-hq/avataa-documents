from datetime import timedelta

from fastapi import APIRouter, HTTPException, Query, Depends
from minio import Minio
from starlette.responses import RedirectResponse

import settings
from database import db
from file_server import minio_client
from schemas.document import Document
from security.security_config import ADMIN_ROLE
from security.security_data_models import UserData
from security.security_factory import security
from security.security_utils import (
    get_available_object_to_read_ids_by_user_data,
)
from utils.document_utils import (
    add_to_query_permission_filter,
    DocumentNotExists,
)

router = APIRouter()


@router.get("/content/{document_id}/{content_id}", include_in_schema=False)
def get_content(
    document_id: str,
    content_id: str,
    version_id: str | None = Query(default=None),
    days: int = Query(default=0, ge=0, le=7),
    hours: int = Query(default=0, ge=0, le=24),
    minutes: int = Query(default=15, ge=0, le=60),
    client: Minio = Depends(minio_client),
    user_data: UserData = Depends(security),
):
    """
    Gets a temporary link from *MINIO* and redirects the user to this link
    Note: Link lifetime cannot exceed 7 days
    \f
    :param document_id: document ID
    :param content_id: content ID
    :param version_id: document version identifier. If not specified, then the latest version is returned.
    :param days: the number of days the link will be available
    :param hours: the number of hours that the link will be available
    :param minutes: the number of minutes that the link will be available
    :param client: minio client
    :param user_data: user data for security
    :return: redirect link
    """
    limit = 7 * 24 * 60
    inputted_limit = days * 24 * 60 + hours * 60 + minutes
    if inputted_limit > limit:
        raise HTTPException(
            status_code=422,
            detail="Please select a valid duration. "
            "This is a temporary URL with integrated access credentials for sharing objects "
            "valid for up to 7 days.",
        )
    try:
        filters = {"id": document_id}

        if ADMIN_ROLE not in user_data.realm_access.roles:
            available_object_ids_by_permission = (
                get_available_object_to_read_ids_by_user_data(
                    user_data=user_data.realm_access
                )
            )
            filters = add_to_query_permission_filter(
                filter_query=filters,
                available_object_ids_by_permission=available_object_ids_by_permission,
            )

        document = db.document.find_one(filters)
        document = Document(**document)
        file_name = "content"
        mime_type = None
        for attachment in document.attachment:
            if content_id == attachment.id:
                file_name = attachment.name
                mime_type = attachment.mime_type
                break
        headers = {
            "response-content-disposition": f'inline; filename="{file_name}"'
        }
        if mime_type is not None and mime_type.lower() != "none":
            headers["response-content-type"] = mime_type
        redirect_link = client.get_presigned_url(
            "GET",
            settings.MINIO_BUCKET,
            f"{document_id}/{content_id}",
            version_id=version_id,
            expires=timedelta(days=days, hours=hours, minutes=minutes),
            response_headers=headers,
        )
        return RedirectResponse(url=redirect_link)
    except Exception as e:
        print(e)  # TODO: logging
        raise HTTPException(status_code=404, detail="File not found")


@router.get(
    "/content/{document_id}/{content_id}/versions", include_in_schema=False
)
def get_versions(
    document_id: str,
    content_id: str,
    client: Minio = Depends(minio_client),
    user_data: UserData = Depends(security),
):
    """
    Returns the available versions for the given document
    \f
    :param document_id: document ID
    :param content_id: content ID
    :param client: minio client
    :param user_data: user data for security
    :return: versions of the document
    """
    try:
        filters = {"id": document_id}

        if ADMIN_ROLE not in user_data.realm_access.roles:
            available_object_ids_by_permission = (
                get_available_object_to_read_ids_by_user_data(
                    user_data=user_data.realm_access
                )
            )
            filters = add_to_query_permission_filter(
                filter_query=filters,
                available_object_ids_by_permission=available_object_ids_by_permission,
            )

        document = db.document.find_one(filters)
        if document:
            resp = client.list_objects(
                settings.MINIO_BUCKET,
                f"{document_id}/{content_id}",
                include_version=True,
            )
            result = [
                {
                    "version_id": v.version_id,
                    "is_delete_marker": v.is_delete_marker,
                    "is_latest": v.is_latest,
                    "last_modified": v.last_modified,
                }
                for v in resp
            ]
            return result

        raise DocumentNotExists

    except Exception as e:
        print(e)  # TODO: logging
        raise HTTPException(status_code=404, detail="File not found")

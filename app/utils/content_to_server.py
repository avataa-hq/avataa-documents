import base64
import io
import sys

import pydantic
from fastapi import HTTPException
from starlette.datastructures import URL

import settings
from database import db
from file_server import minio_client
from schemas.document import Document, ChangeDocument
from schemas.document_specification import (
    DocumentSpecification,
    ChangeDocumentSpecification,
)
from schemas.document_status_type import DocumentStatusType
from settings import API_VERSION
from utils.merge_json import merge


def replace_content_with_link(
    document: Document | DocumentSpecification, base_url
):
    if document.attachment is None:
        return
    for attachment in document.attachment:
        if attachment.content is not None:
            decoded_attachment = base64.b64decode(
                attachment.content, validate=True
            )
            buf = io.BytesIO(decoded_attachment)
            try:
                attachment.mime_type.encode("latin-1")
            except Exception as e:
                print(e, file=sys.stderr)
                raise HTTPException(status_code=422, detail="Mime type error")
            try:
                minio_client().put_object(
                    bucket_name=settings.MINIO_BUCKET,
                    object_name=f"{document.id}/{attachment.id}",
                    data=buf,
                    length=buf.getbuffer().nbytes,
                    content_type=attachment.mime_type,
                )
            except Exception as e:
                print(e, file=sys.stderr)
                raise HTTPException(
                    status_code=422, detail="The file could not be saved"
                )
            attachment.content = None
            print(base_url)
            attachment.url = f"{base_url}v{API_VERSION}/content/{document.id}/{attachment.id}"
    return document


def drop_old_content(
    old_document: Document | DocumentSpecification,
    new_document: Document
    | ChangeDocument
    | DocumentSpecification
    | ChangeDocumentSpecification = None,
):
    if old_document.attachment is None:
        return

    if new_document is None:
        objects_to_delete = minio_client().list_objects(
            bucket_name=settings.MINIO_BUCKET,
            prefix=old_document.id,
            recursive=True,
        )
        for obj in objects_to_delete:
            minio_client().remove_object(
                bucket_name=settings.MINIO_BUCKET, object_name=obj.object_name
            )
        return

    if new_document.attachment is None:
        new_att = []
    else:
        new_att = [att.id for att in new_document.attachment]
    for old_att in old_document.attachment:
        if old_att.id not in new_att:
            minio_client().remove_object(
                bucket_name=settings.MINIO_BUCKET,
                object_name=f"{old_document.id}/{old_att.id}",
            )


def drop_document_data(document: dict, base_url: str | URL, document_id: str):
    document = pydantic.parse_obj_as(Document, document)
    drop_old_content(document)
    changed_document = ChangeDocument(status=DocumentStatusType.DELETED)
    old_document = db.document.find_one({"id": document_id})
    if old_document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    patch_document_data(
        old_document=old_document,
        document=changed_document,
        base_url=base_url,
        document_id=document_id,
    )


def patch_document_data(
    document: ChangeDocument,
    old_document: dict | Document,
    base_url: str | URL,
    document_id: str,
):
    new_document = merge(
        old_document, document.dict(by_alias=True, exclude_unset=True)
    )
    old_document = Document(**old_document)
    new_document = Document(**new_document)

    drop_old_content(old_document, new_document)

    replace_content_with_link(new_document, base_url)
    db.document.replace_one(
        {"id": document_id}, new_document.dict(exclude_none=True, by_alias=True)
    )
    return new_document

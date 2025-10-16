import pathlib
from datetime import datetime

from fastapi import UploadFile

from schemas.attachment_ref_or_value import AttachmentRefOrValue
from schemas.document import Document
from schemas.document_status_type import DocumentStatusType
from schemas.external_identifier import ExternalIdentifier
from schemas.quantity import Quantity
from settings import INVENTORY_OBJECT_PREFIX, API_VERSION

b_to_mb_coefficient = 1_000_000


def create_document_with_attachment(
    mo_id: int,
    attachment: UploadFile,
    now: datetime,
    base_url: str,
    attachment_id: str | None = None,
) -> Document:
    external_identifier_href = f"{INVENTORY_OBJECT_PREFIX}{mo_id}"
    external_identifier = ExternalIdentifier(
        id=str(mo_id), owner="", href=external_identifier_href
    )
    document = Document(
        name=attachment.filename,
        status=DocumentStatusType.CREATED.value,
        lastUpdate=now,
        creationDate=now,
        externalIdentifier=[external_identifier],
    )
    document.href = f"{base_url}v{API_VERSION}/document/{document.id}"
    attachment_doc = create_attachment(
        attachment=attachment,
        document=document,
        base_url=base_url,
        attachment_id=attachment_id,
    )
    if not document.attachment:
        document.attachment = []
    document.attachment.append(attachment_doc)
    return document


def create_attachment(
    document: Document,
    attachment: UploadFile,
    base_url: str,
    attachment_id: str | None = None,
) -> AttachmentRefOrValue:
    path = pathlib.Path(attachment.filename)
    file_name = path.name
    file_extension = path.suffix
    if file_extension:
        file_extension = file_extension[1:]
    file_size = Quantity(
        amount=round(attachment.size / b_to_mb_coefficient, 2), units="MB"
    )
    attachment_doc = AttachmentRefOrValue(
        name=file_name,
        attachmentType=file_extension,
        mimeType=attachment.content_type,
        size=file_size,
    )
    if attachment_id:
        attachment_doc.id = attachment_id
    attachment_doc.url = (
        f"{base_url}v{API_VERSION}/content/{document.id}/{attachment_doc.id}"
    )
    return attachment_doc


def delete_attachment(document: Document, file: UploadFile):
    deleted_attachment = None
    if not file:
        return deleted_attachment
    for attachment_doc in document.attachment:
        if attachment_doc.name == file.filename:
            deleted_attachment = attachment_doc
            break
    if deleted_attachment:
        document.attachment.remove(deleted_attachment)
    return deleted_attachment

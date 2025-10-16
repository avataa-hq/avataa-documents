from datetime import datetime
from typing import Annotated, List

from fastapi import APIRouter, HTTPException, Depends, Path, Query, UploadFile
from fastapi.requests import Request
from minio import Minio, S3Error
from minio.commonconfig import CopySource
from starlette.status import HTTP_507_INSUFFICIENT_STORAGE

import settings
from database import db
from file_server import minio_client
from kafka import kafka_document_pb2
from kafka.consumer.kafka_producer import (
    get_documents_kafka_producer_factory_method,
    KafkaProducerInterface,
)
from schemas.document import Document, ResponseDocument
from schemas.document_status_type import DocumentStatusType
from security.security_config import ADMIN_ROLE
from security.security_data_models import UserData
from security.security_factory import security
from security.security_utils import (
    get_available_object_to_read_ids_by_user_data,
    get_available_object_to_create_ids_by_user_data,
    get_available_object_to_update_ids_by_user_data,
    get_available_object_to_delete_ids_by_user_data,
)
from tasks.create_document_with_attachments import (
    create_document_with_attachment,
    delete_attachment,
)
from tasks.find_document_by_id_and_attachment_name import (
    find_document_by_id_and_attachment_name,
)
from tasks.remove_object_version import remove_object_latest_version
from tasks.upload_attachment import upload_attachment
from utils.content_to_server import drop_document_data
from utils.document_utils import add_to_query_permission_filter
from utils.kafka import DocumentsStatus, send_to_kafka

router = APIRouter()


@router.post(
    "/copy_between_objects",
    response_model=list[ResponseDocument],
    tags=["Inventory"],
    response_model_exclude_none=True,
)
def copy_attachments(
    from_mo_id: int,
    to_mo_id: int,
    client: Minio = Depends(minio_client),
    user_data: UserData = Depends(security),
):
    from_mo_id = str(from_mo_id)
    to_mo_id = str(to_mo_id)

    already_existing_mo_documents_filter = {"externalIdentifier.id": to_mo_id}
    if ADMIN_ROLE not in user_data.realm_access.roles:
        filter_query = get_available_object_to_read_ids_by_user_data(
            user_data=user_data.realm_access
        )
        already_existing_mo_documents_filter = add_to_query_permission_filter(
            filter_query=already_existing_mo_documents_filter,
            available_object_ids_by_permission=filter_query,
        )

    existing_documents = db.document.find(already_existing_mo_documents_filter)
    already_existing_mo_attachment_ids = set()
    for document in existing_documents:
        document = Document.validate(document)
        for attachment in document.attachment:
            already_existing_mo_attachment_ids.add(attachment.id)

    filters = {
        "status": {"$ne": "deleted"},
        "externalIdentifier.id": from_mo_id,
    }
    if ADMIN_ROLE not in user_data.realm_access.roles:
        filter_query = get_available_object_to_read_ids_by_user_data(
            user_data=user_data.realm_access
        )
        filters = add_to_query_permission_filter(
            filter_query=filters,
            available_object_ids_by_permission=filter_query,
        )

    documents = db.document.find(filters)
    current_datetime = datetime.utcnow()
    results = []
    for document in documents:
        # mongodb
        old_document_id = document.pop("id")
        document = Document.validate(document)
        document.creation_date = current_datetime
        document.last_update = current_datetime
        document.status = DocumentStatusType.CREATED

        new_external_identifier = []
        for external_identifier in document.external_identifier:
            if external_identifier.id != from_mo_id:
                continue
            external_identifier.href = external_identifier.href.replace(
                from_mo_id, to_mo_id
            )
            external_identifier.id = to_mo_id
            new_external_identifier.append(external_identifier)
        document.external_identifier = new_external_identifier

        new_attachment = []
        for attachment in document.attachment:
            if attachment.id in already_existing_mo_attachment_ids:
                continue

            attachment.url = attachment.url.replace(
                old_document_id, document.id
            )

            # minio
            source = CopySource(
                bucket_name=settings.MINIO_BUCKET,
                object_name=f"{old_document_id}/{attachment.id}",
            )
            try:
                client.copy_object(
                    bucket_name=settings.MINIO_BUCKET,
                    object_name=f"{document.id}/{attachment.id}",
                    source=source,
                )
            except S3Error as e:
                for new_att in new_attachment:
                    client.remove_object(
                        bucket_name=settings.MINIO_BUCKET,
                        object_name=f"{document.id}/{new_att.id}",
                    )
                raise HTTPException(status_code=500, detail=e.message)
            else:
                new_attachment.append(attachment)
        if not new_attachment:
            continue
        document.attachment = new_attachment

        if ADMIN_ROLE not in user_data.realm_access.roles and document:
            filter_query = get_available_object_to_create_ids_by_user_data(
                user_data=user_data.realm_access
            )
            if str(document) not in filter_query:
                raise HTTPException(
                    status_code=500,
                    detail="Access denied: the current user lacks the necessary "
                    "permissions to perform this action.",
                )

        db.document.insert_one(
            document=document.dict(exclude_none=True, by_alias=True)
        )
        results.append(document.dict(exclude_none=True, by_alias=True))

        # kafka
        mo_ids = [int(e_i.id) for e_i in document.external_identifier]
        data = kafka_document_pb2.Document(mo_id=mo_ids)
        send_to_kafka(
            data=data,
            topic=settings.KAFKA_PRODUCER_TOPIC,
            key=DocumentsStatus.CREATED.value,
        )
    return results


@router.post(
    "/inventory/object/{mo_id}",
    response_model=list[ResponseDocument],
    tags=["Inventory"],
)
def add_attachments_to_mo_id(
    request: Request,
    mo_id: Annotated[int, Path(gt=0)],
    attachments: list[UploadFile],
    client: Minio = Depends(minio_client),
    kfk_producer=Depends(get_documents_kafka_producer_factory_method),
    user_data: UserData = Depends(security),
):
    create_documents: list[Document] = []
    update_documents: list[Document] = []
    now = datetime.utcnow()
    try:
        for attachment in attachments:
            print(attachment.filename)
            exists_documents = find_document_by_id_and_attachment_name(
                attachment_name=attachment.filename, mo_id=mo_id
            )
            if exists_documents:
                document = exists_documents[0]
                deleted_attachment = delete_attachment(
                    document=document, file=attachment
                )
                document = create_document_with_attachment(
                    attachment=attachment,
                    mo_id=mo_id,
                    now=now,
                    base_url=str(request.base_url),
                    attachment_id=deleted_attachment.id,
                )
            else:
                document = create_document_with_attachment(
                    attachment=attachment,
                    mo_id=mo_id,
                    now=now,
                    base_url=str(request.base_url),
                )
            upload_attachment(
                document_id=document.id,
                attachment_id=document.attachment[-1].id,
                client=client,
                file=attachment,
            )
            if exists_documents:
                update_documents.append(document)
            else:
                create_documents.append(document)
    except S3Error:
        for result in create_documents:
            drop_document_data(
                document=result.dict(by_alias=True, exclude_none=True),
                document_id=result.id,
                base_url=request.base_url,
            )
        for result in update_documents:
            remove_object_latest_version(
                document_id=result.id,
                attachment_id=result.attachment[-1].id,
                client=client,
            )
        raise HTTPException(
            status_code=HTTP_507_INSUFFICIENT_STORAGE,
            detail="Insufficient Storage",
        )
    results = []
    if create_documents:
        if ADMIN_ROLE not in user_data.realm_access.roles:
            available_object_ids_by_permission = (
                get_available_object_to_create_ids_by_user_data(
                    user_data=user_data.realm_access
                )
            )
            if str(mo_id) not in available_object_ids_by_permission:
                raise HTTPException(
                    status_code=500,
                    detail="Access denied: the current user lacks the necessary "
                    "permissions to perform this action.",
                )

        db.document.insert_many(
            [i.dict(by_alias=True, exclude_none=True) for i in create_documents]
        )
        results.extend(create_documents)
        kfk_producer.send_created_attachments_by_doc(docs=create_documents)

    if update_documents:
        if ADMIN_ROLE not in user_data.realm_access.roles:
            available_object_ids_by_permission = (
                get_available_object_to_update_ids_by_user_data(
                    user_data=user_data.realm_access
                )
            )
            if str(mo_id) not in available_object_ids_by_permission:
                raise HTTPException(
                    status_code=500,
                    detail="Access denied: the current user lacks the necessary "
                    "permissions to perform this action.",
                )

        for upd_doc in update_documents:
            db.document.replace_one(
                filter={"id": upd_doc.id},
                replacement=upd_doc.dict(exclude_none=True, by_alias=True),
            )
        results.extend(update_documents)
    return results


@router.get(
    "/inventory/object/{mo_id}",
    response_model=List[ResponseDocument],
    tags=["Inventory"],
)
def get_documents_by_mo_id(
    mo_id: Annotated[int, Path(gt=0)],
    status: Annotated[list[str], None] = Query(None),
    user_data: UserData = Depends(security),
):
    query = {"externalIdentifier.id": str(mo_id)}
    if status:
        query["status"] = {"$in": [st for st in status]}

    if ADMIN_ROLE not in user_data.realm_access.roles:
        available_object_ids_by_permission = (
            get_available_object_to_read_ids_by_user_data(
                user_data=user_data.realm_access
            )
        )
        query = add_to_query_permission_filter(
            filter_query=query,
            available_object_ids_by_permission=available_object_ids_by_permission,
        )
    response = db.document.find(query)
    results = [ResponseDocument(**i) for i in response]
    return results


@router.delete(
    "/inventory/object/{mo_id}",
    response_model=None,
    tags=["Inventory"],
)
def delete_documents_by_mo_id(
    mo_id: Annotated[int, Path(gt=0)],
    client: Minio = Depends(minio_client),
    kfk_producer: KafkaProducerInterface = Depends(
        get_documents_kafka_producer_factory_method
    ),
    user_data: UserData = Depends(security),
):
    if ADMIN_ROLE not in user_data.realm_access.roles:
        available_object_ids_by_permission = (
            get_available_object_to_delete_ids_by_user_data(
                user_data=user_data.realm_access
            )
        )

        if str(mo_id) in available_object_ids_by_permission:
            raise HTTPException(
                status_code=500,
                detail="Access denied: the current user lacks the necessary "
                "permissions to perform this action.",
            )

    query = {"externalIdentifier": str(mo_id)}

    response = db.document.find(query)
    results = [Document(**i) for i in response]
    file_urls: list[str] = []
    documents_to_update: list[Document] = []
    documents_to_update_kafka: list[Document] = []
    documents_to_delete: list[Document] = []
    for document in results:
        if len(document.external_identifier) == 1:
            documents_to_delete.append(document)
            if document.attachment:
                for attachment in document.attachment:
                    file_url = f"{document.id}/{attachment.id}"
                    file_urls.append(file_url)
        else:
            kafka_document = document.copy(deep=True)
            kafka_document.external_identifier = [
                i for i in document.external_identifier if i.id == str(mo_id)
            ]
            documents_to_update_kafka.append(kafka_document)

            document.external_identifier = [
                i for i in document.external_identifier if i.id != str(mo_id)
            ]
            documents_to_update.append(document)
    if file_urls:
        client.remove_objects(
            settings.MINIO_BUCKET, delete_object_list=file_urls
        )
    if documents_to_delete:
        document_ids = [i.id for i in documents_to_delete]
        query = {"id": {"$in": document_ids}}
        db.document.delete_many(query)
        kfk_producer.send_deleted_attachments_by_doc(docs=documents_to_delete)
    if documents_to_update:
        for upd_doc in documents_to_update:
            db.document.replace_one(
                filter={"id": upd_doc.id},
                replacement=upd_doc.dict(exclude_none=True, by_alias=True),
            )
        kfk_producer.send_deleted_attachments_by_doc(
            docs=documents_to_update_kafka
        )

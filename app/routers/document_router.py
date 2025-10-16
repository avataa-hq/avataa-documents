from typing import Annotated

from fastapi import APIRouter, Depends, Path, HTTPException
from fastapi.requests import Request
from fastapi.responses import Response
from pymongo.cursor import Cursor

from database import db
from kafka.consumer.kafka_producer import (
    get_documents_kafka_producer_factory_method,
)
from schemas.document import Document, ChangeDocument, ResponseDocument
from security.security_config import ADMIN_ROLE
from security.security_data_models import UserData
from security.security_factory import security
from security.security_utils import (
    get_available_object_to_read_ids_by_user_data,
    get_available_object_to_create_ids_by_user_data,
    get_available_object_to_update_ids_by_user_data,
    get_available_object_to_delete_ids_by_user_data,
)
from settings import API_VERSION
from utils.content_to_server import (
    replace_content_with_link,
    patch_document_data,
    drop_document_data,
)
from utils.document_utils import add_to_query_permission_filter
from utils.parser import parse_query_wrapper

router = APIRouter()


@router.get(
    "/document",
    response_model=list[ResponseDocument],
    tags=["Document"],
    response_model_exclude_none=True,
)
def list_documents(
    response: Response,
    data: dict = Depends(parse_query_wrapper(ChangeDocument)),
    user_data: UserData = Depends(security),
):
    """
    This operation list document entities.
    Attribute selection is enabled for all first level attributes.
    Filtering may be available depending on the compliance level supported by an implementation.
    \f
    :param response: response, used to change headers
    :param data: user request parsed using a self-written parser
    :param user_data: user data for security
    :return: list of ResponseDocument
    """
    offset = data.get("offset", None)
    limit = data.get("limit", None)
    filters = data.get("filters", {})
    fields = data.get("fields", [])
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

    resp: Cursor = db.document.find(filters, fields)

    if offset:
        resp = resp.skip(offset)
    if limit:
        resp = resp.limit(limit)
    res = list(r for r in resp)
    response.headers["X-Result-Count"] = str(len(res))
    response.headers["X-Total-Count"] = str(
        db.document.count_documents(filters)
    )
    return res


@router.get(
    "/document/{id}", response_model=ResponseDocument, tags=["Document"]
)
def retrieve_document(
    id: str = Path(alias="id"),
    data: dict = Depends(parse_query_wrapper(ChangeDocument)),
    user_data: UserData = Depends(security),
):
    """
    This operation retrieves a document entity.
    Attribute selection is enabled for all first level attributes.
    Filtering on sub-resources may be available depending on the compliance level supported by an implementation.
    \f
    :param id: document ID
    :param data: user request parsed using a self-written parser
    :param user_data: user data for security
    :return: list of ResponseDocument
    """
    filters = data.get("filters", {})
    filters["id"] = id
    fields = data.get("fields", [])
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

    result = db.document.find_one(filters, fields)
    if not result:
        raise HTTPException(status_code=404, detail="Document not found")
    return result


@router.post(
    "/document",
    response_model=ResponseDocument,
    tags=["Document"],
    response_model_exclude_none=True,
    status_code=201,
)
async def create_document(
    document: Document,
    request: Request,
    kfk_producer=Depends(get_documents_kafka_producer_factory_method),
    user_data: UserData = Depends(security),
):
    """
    This operation creates a document entity.
    \f
    :param document: Document
    :param request: http connection
    :param user_data: user data for security
    :param kfk_producer: kafka producer
    :return: Document with id
    """
    if (
        document.id is not None
        and db.document.find_one({"id": document.id}) is not None
    ):
        raise HTTPException(
            status_code=409, detail="Document with this ID already exists"
        )
    if document.href is None:
        document.href = (
            f"{request.base_url}v{API_VERSION}/document/{document.id}"
        )
    replace_content_with_link(document, request.base_url)

    document_to_create = document.dict(exclude_none=True, by_alias=True)
    document_object_id = document_to_create.get("externalIdentifier", [{}])[
        0
    ].get("id")

    if ADMIN_ROLE not in user_data.realm_access.roles and document_object_id:
        available_object_ids_by_permission = (
            get_available_object_to_create_ids_by_user_data(
                user_data=user_data.realm_access
            )
        )
        if str(document_object_id) not in available_object_ids_by_permission:
            raise HTTPException(
                status_code=500,
                detail="Access denied: the current user lacks the necessary "
                "permissions to perform this action.",
            )

    resp = db.document.insert_one(
        document=document.dict(exclude_none=True, by_alias=True)
    )
    if not resp.acknowledged:
        raise HTTPException(status_code=500, detail="document not saved")
    kfk_producer.send_created_attachments_by_doc(docs=[document])
    return document


@router.patch(
    "/document/{id}",
    response_model=Document,
    tags=["Document"],
    response_model_exclude_none=True,
)
def patch_document(
    request: Request,
    document: ChangeDocument,
    id: str = Path(alias="id"),
    user_data: UserData = Depends(security),
):
    """
    This operation allows partial updates of a document entity. Support of json/merge
    (https://tools.ietf.org/html/rfc7386) is mandatory, support of json/patch
    (http://tools.ietf.org/html/rfc5789) is optional.
    Note: If the update operation yields to the creation of sub-resources or relationships,
    the same rules concerning mandatory sub-resource attributes and default value settings in the POST operation applies
    to the PATCH operation.  Hence, these tables are not repeated here.
    \f
    :param id: Document ID
    :param document: ChangeDocument
    :param request: http connection
    :param user_data: user data for security
    :return: changed Document
    """
    old_document = db.document.find_one({"id": id})
    if old_document is None:
        raise HTTPException(status_code=404, detail="Document not found")

    document_linked_to_object = old_document.get("externalIdentifier", [{}])[
        0
    ].get("id")
    if (
        ADMIN_ROLE not in user_data.realm_access.roles
        and document_linked_to_object
    ):
        available_object_ids_by_permission = (
            get_available_object_to_update_ids_by_user_data(
                user_data=user_data.realm_access
            )
        )
        if (
            str(document_linked_to_object)
            not in available_object_ids_by_permission
        ):
            raise HTTPException(
                status_code=500,
                detail="Access denied: the current user lacks the necessary "
                "permissions to perform this action.",
            )

    new_document = patch_document_data(
        old_document=old_document,
        document=document,
        base_url=request.base_url,
        document_id=id,
    )
    return new_document


@router.delete(
    "/document/{id}",
    response_class=Response,
    tags=["Document"],
    status_code=204,
)
def delete_document(
    request: Request,
    id: Annotated[str, Path(alias="id")],
    kfk_producer=Depends(get_documents_kafka_producer_factory_method),
    user_data: UserData = Depends(security),
):
    """
    This operation deletes a document entity.
    \f
    :param id: Document ID
    """
    document = db.document.find_one({"id": id})
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")

    document_linked_to_object = document.get("externalIdentifier", [{}])[0].get(
        "id"
    )
    if (
        ADMIN_ROLE not in user_data.realm_access.roles
        and document_linked_to_object
    ):
        available_object_ids_by_permission = (
            get_available_object_to_delete_ids_by_user_data(
                user_data=user_data.realm_access
            )
        )
        if (
            str(document_linked_to_object)
            not in available_object_ids_by_permission
        ):
            raise HTTPException(
                status_code=500,
                detail="Access denied: the current user lacks the necessary "
                "permissions to perform this action.",
            )

    drop_document_data(
        document=document, document_id=id, base_url=request.base_url
    )
    # document = Document(**document)
    # kfk_producer.send_deleted_attachments_by_doc(docs=[document])

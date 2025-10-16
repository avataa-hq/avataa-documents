import pydantic
from fastapi import APIRouter, Depends, Path, HTTPException
from pymongo.cursor import Cursor
from fastapi.responses import Response
from fastapi.requests import Request

from database import db
from schemas.document_specification import (
    DocumentSpecification,
    ChangeDocumentSpecification,
    ResponseDocumentSpecification,
)
from settings import API_VERSION
from utils.content_to_server import replace_content_with_link, drop_old_content
from utils.merge_json import merge
from utils.parser import parse_query_wrapper

router = APIRouter()


@router.get(
    "/documentSpecification",
    response_model=list[ResponseDocumentSpecification],
    tags=["DocumentSpecification"],
)
def list_document_specifications(
    response: Response,
    data: dict = Depends(parse_query_wrapper(ChangeDocumentSpecification)),
):
    """
    This operation list document specification entities.
    Attribute selection is enabled for all first level attributes.
    Filtering may be available depending on the compliance level supported by an implementation.
    \f
    :param response: response, used to change headers
    :param data: user request parsed using a self-written parser
    :return: list of ResponseDocumentSpecification
    """
    offset = data.get("offset", None)
    limit = data.get("limit", None)
    filters = data.get("filters", {})
    fields = data.get("fields", [])
    resp: Cursor = db.document_specification.find(filters, fields)
    if offset:
        resp = resp.skip(offset)
    if limit:
        resp = resp.limit(limit)
    res = list(r for r in resp)
    response.headers["X-Result-Count"] = str(len(res))
    response.headers["X-Total-Count"] = str(
        db.document_specification.count_documents(filters)
    )
    return res


@router.get(
    "/documentSpecification/{id}",
    response_model=ResponseDocumentSpecification,
    tags=["DocumentSpecification"],
)
def retrieve_document_specification(
    id: str = Path(alias="id"),
    data: dict = Depends(parse_query_wrapper(ChangeDocumentSpecification)),
):
    """
    This operation retrieves a document specification entity.
    Attribute selection is enabled for all first level attributes.
    Filtering on sub-resources may be available depending on the compliance level supported by an implementation.
    \f
    :param id: document specification ID
    :param data: user request parsed using a self-written parser
    :return: list of ResponseDocument
    """
    filters = data.get("filters", {})
    filters["id"] = id
    fields = data.get("fields", [])
    result = db.document_specification.find_one(filters, fields)
    if not result:
        raise HTTPException(
            status_code=404, detail="Document specification not found"
        )
    return result


@router.post(
    "/documentSpecification",
    response_model=DocumentSpecification,
    tags=["DocumentSpecification"],
    response_model_exclude_none=True,
    status_code=201,
)
def create_document_specification(
    request: Request, document_spec: DocumentSpecification
):
    """
    This operation creates a document specification entity.
    \f
    :param document_spec: Document specification
    :return: Document specification with id
    """
    if (
        document_spec.id is not None
        and db.document_specification.find_one({"id": document_spec.id})
        is not None
    ):
        raise HTTPException(
            status_code=409, detail="Document with this ID already exists"
        )
    attachment = document_spec.attachment
    document_spec.attachment = None
    resp = db.document_specification.insert_one(
        document=document_spec.dict(exclude_none=True, by_alias=True)
    )

    document_id = (
        str(resp.inserted_id) if not document_spec.id else document_spec.id
    )
    href = (
        f"{request.base_url}v{API_VERSION}/documentSpecification/{document_id}"
    )
    document_spec.id = document_id
    document_spec.href = href
    document_spec.attachment = attachment
    replace_content_with_link(document_spec, request.base_url)
    if document_spec.attachment is None:
        att_dict = None
    else:
        att_dict = [
            att.dict(by_alias=True, exclude_none=True)
            for att in document_spec.attachment
        ]
    db.document_specification.update_one(
        filter={"_id": resp.inserted_id},
        update={
            "$set": {
                "id": document_spec.id,
                "href": document_spec.href,
                "attachment": att_dict,
            }
        },
    )
    return document_spec


@router.patch(
    "/documentSpecification/{id}",
    response_model=DocumentSpecification,
    tags=["DocumentSpecification"],
    response_model_exclude_none=True,
)
def patch_document_specification(
    request: Request,
    document_spec: ChangeDocumentSpecification,
    id: str = Path(alias="id"),
):
    """
    This operation allows partial updates of a document specification entity. Support of json/merge
    (https://tools.ietf.org/html/rfc7386) is mandatory, support of json/patch (http://tools.ietf.org/html/rfc5789)
    is optional.
    Note: If the update operation yields to the creation of sub-resources or relationships, the same rules concerning
    mandatory sub-resource attributes and default value settings in the POST operation applies to the PATCH operation.
    Hence, these tables are not repeated here.
    \f
    :param _id: Document specification ID
    :param document_spec: ChangeDocumentSpecification
    :return: changed DocumentSpecification
    """
    old_document_spec = db.document_specification.find_one({"id": id})
    if old_document_spec is None:
        raise HTTPException(status_code=404, detail="Document not found")
    new_document_spec = merge(
        old_document_spec, document_spec.dict(by_alias=True, exclude_unset=True)
    )

    old_document_spec = DocumentSpecification(**old_document_spec)
    new_document_spec = DocumentSpecification(**new_document_spec)

    drop_old_content(old_document_spec, document_spec)

    replace_content_with_link(new_document_spec, request.base_url)
    db.document_specification.replace_one(
        {"id": id}, new_document_spec.dict(exclude_none=True, by_alias=True)
    )
    return new_document_spec


@router.delete(
    "/documentSpecification/{id}",
    response_class=Response,
    tags=["DocumentSpecification"],
    status_code=204,
)
def delete_document_specification(id: str = Path(alias="id")):
    """
    This operation deletes a document_spec specification entity.
    \f
    :param id: Document specification ID
    """
    document_spec = db.document_specification.find_one({"id": id})
    if document_spec is None:
        raise HTTPException(status_code=404, detail="Document not found")
    document_spec = pydantic.parse_obj_as(DocumentSpecification, document_spec)
    drop_old_content(document_spec)
    db.document_specification.delete_one({"id": id})

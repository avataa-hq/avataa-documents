import uuid
from datetime import datetime

from pydantic import BaseModel, AnyUrl, Field

from schemas.attachment_ref_or_value import AttachmentRefOrValue
from schemas.category_ref import CategoryRef
from schemas.characteristic import Characteristic
from schemas.document_ref import DocumentRef
from schemas.document_specification_ref_or_value import (
    DocumentSpecificationRefOrValue,
)
from schemas.document_status_type import DocumentStatusType
from schemas.external_identifier import ExternalIdentifier
from schemas.load_field_description import field_description
from schemas.related_entity import RelatedEntity
from schemas.related_party import RelatedParty

fd = field_description["Document"]


class ChangeDocument(BaseModel):
    """
    Used to modify an already existing document
    """

    attachment: list[AttachmentRefOrValue] | None = Field(
        default=None, description=fd["attachment"]
    )
    category: list[CategoryRef] | None = Field(
        default=None, description=fd["category"]
    )
    characteristic: list[Characteristic] | None = Field(
        default=None, description=fd["characteristic"]
    )
    creation_date: datetime | None = Field(
        default=None, alias="creationDate", description=fd["creationDate"]
    )
    description: str | None = Field(default=None, description=fd["description"])
    document: list[DocumentRef] | None = Field(
        default=None, description=fd["document"]
    )
    document_specification: DocumentSpecificationRefOrValue | None = Field(
        default=None,
        alias="documentSpecification",
        description=fd["documentSpecification"],
    )
    document_type: str | None = Field(
        default=None, alias="documentType", description=fd["documentType"]
    )
    external_identifier: list[ExternalIdentifier] | None = Field(
        default=None,
        alias="externalIdentifier",
        description=fd["externalIdentifier"],
    )
    last_update: datetime | None = Field(
        default_factory=datetime.now,
        alias="lastUpdate",
        description=fd["lastUpdate"],
    )
    name: str | None = Field(default=None, description=fd["name"])
    related_entity: list[RelatedEntity] | None = Field(
        default=None, alias="relatedEntity", description=fd["relatedEntity"]
    )
    related_party: list[RelatedParty] | None = Field(
        default=None, alias="relatedParty", description=fd["relatedParty"]
    )
    status: DocumentStatusType | None = Field(
        default=None, description=fd["status"]
    )
    version: str | None = Field(default=None, description=fd["version"])

    class Config:
        use_enum_values = True


class Document(ChangeDocument):
    """
    The document is the main element for displaying and interacting with the microservice
    """

    href: AnyUrl | None = Field(default=None, description=fd["href"])
    id: str | None = Field(
        default_factory=lambda: str(uuid.uuid4()), description=fd["id"]
    )
    base_type: str | None = Field(
        default=None, alias="@baseType", description=fd["@baseType"]
    )
    schema_location: AnyUrl | None = Field(
        default=None, alias="@schemaLocation", description=fd["@schemaLocation"]
    )
    type: str | None = Field(
        default=None, alias="@type", description=fd["@type"]
    )
    name: str = Field(description=fd["name"])
    creation_date: datetime | None = Field(
        default_factory=datetime.now,
        alias="creationDate",
        description=fd["creationDate"],
    )
    status: DocumentStatusType | None = Field(
        default=DocumentStatusType.CREATED, description=fd["status"]
    )

    @classmethod
    def get_field_names(cls, alias=False):
        return list(cls.schema(alias).get("properties").keys())

    class Config:
        use_enum_values = True


class ResponseDocument(Document):
    """
    Used to return to the user
    """

    name: str | None = Field(default=None, description=fd["name"])

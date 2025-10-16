from datetime import datetime

from pydantic import BaseModel, Field, AnyUrl

from schemas.attachment_ref_or_value import AttachmentRefOrValue
from schemas.characteristic_specification import CharacteristicSpecification
from schemas.constraint_ref import ConstraintRef
from schemas.document_specification_status_type import (
    DocumentSpecificationStatusType,
)
from schemas.entity_specification_relationship import (
    EntitySpecificationRelationship,
)
from schemas.load_field_description import field_description
from schemas.related_party import RelatedParty
from schemas.target_entity_schema import TargetEntitySchema
from schemas.time_period import TimePeriod

fd = field_description["DocumentSpecification"]


class ChangeDocumentSpecification(BaseModel):
    """
    Used to modify an already existing document specification
    """

    description: str | None = Field(default=None, description=fd["description"])
    is_bundle: bool | None = Field(
        default=None, alias="isBundle", description=fd["isBundle"]
    )
    last_update: datetime | None = Field(
        default=None, alias="lastUpdate", description=fd["lastUpdate"]
    )
    lifecycleStatus: DocumentSpecificationStatusType | None = Field(
        default=None, alias="lifecycleStatus", description=fd["lifecycleStatus"]
    )
    name: str | None = Field(default=None, description=fd["name"])
    version: str | None = Field(default=None, description=fd["version"])
    attachment: list[AttachmentRefOrValue] | None = Field(
        default=None, description=fd["attachment"]
    )
    constraint: list[ConstraintRef] | None = Field(
        default=None, description=fd["constraint"]
    )
    entity_spec_relationship: list[EntitySpecificationRelationship] | None = (
        Field(
            default=None,
            alias="entitySpecRelationship",
            description=fd["entitySpecRelationship"],
        )
    )
    related_party: list[RelatedParty] | None = Field(
        default=None, alias="relatedParty", description=fd["relatedParty"]
    )
    spec_characteristic: list[CharacteristicSpecification] | None = Field(
        default=None,
        alias="specCharacteristic",
        description=fd["specCharacteristic"],
    )
    target_entity_schema: TargetEntitySchema | None = Field(
        default=None,
        alias="targetEntitySchema",
        description=fd["targetEntitySchema"],
    )
    valid_for: TimePeriod | None = Field(
        default=None, alias="validFor", description=fd["validFor"]
    )


class DocumentSpecification(ChangeDocumentSpecification):
    """
    The document specification is the main element for displaying and interacting with the microservice
    """

    name: str = Field(description=fd["name"])
    href: AnyUrl | None = Field(default=None, description=fd["href"])
    id: str | None = Field(default=None, description=fd["id"])
    base_type: str | None = Field(
        default=None, alias="@baseType", description=fd["@baseType"]
    )
    schema_location: AnyUrl | None = Field(
        default=None, alias="@schemaLocation", description=fd["@schemaLocation"]
    )
    type: str | None = Field(
        default=None, alias="@type", description=fd["@type"]
    )

    @classmethod
    def get_field_names(cls, alias=False):
        return list(cls.schema(alias).get("properties").keys())

    class Config:
        use_enum_values = True


class ResponseDocumentSpecification(DocumentSpecification):
    """
    Used to return to the user
    """

    name: str | None = Field(default=None, description=fd["name"])

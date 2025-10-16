from pydantic import BaseModel, Field, AnyUrl

from schemas.load_field_description import field_description

fd = field_description["ExternalIdentifier"]


class ExternalIdentifier(BaseModel):
    """
    An identification of an entity that is owned by or originates in a software system different from the current
    system, for example a ProductOrder handed off from a commerce platform into an order handling system. The structure
    identifies the system itself, the nature of the entity within the system (e.g., class name) and the unique ID of the
    entity within the system. It is anticipated that multiple external IDs can be held for a single entity, e.g., if the
    entity passed through multiple systems on the way to the current system. In this case the consumer is expected to
    sequence the IDs in the array in reverse order of provenance, i.e., most recent system first in the list.
    """

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
    external_identifier_type: str | None = Field(
        default=None,
        alias="externalIdentifierType",
        description=fd["externalIdentifierType"],
    )
    owner: str | None = Field(default=None, description=fd["owner"])

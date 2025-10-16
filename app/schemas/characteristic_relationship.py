import uuid

from pydantic import BaseModel, Field, AnyUrl

from schemas.load_field_description import field_description

fd = field_description["CharacteristicRelationship"]


class CharacteristicRelationship(BaseModel):
    """
    Another Characteristic that is related to the current Characteristic.
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
    relationship_type: str | None = Field(
        default=None,
        alias="relationshipType",
        description=fd["relationshipType"],
    )

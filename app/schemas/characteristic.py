import uuid

from pydantic import BaseModel, Field, AnyUrl, types

from schemas.characteristic_relationship import CharacteristicRelationship
from schemas.load_field_description import field_description

fd = field_description["Characteristic"]


class Characteristic(BaseModel):
    """
    Describes a given characteristic of an object or entity through a name/value pair.
    """

    base_type: str | None = Field(
        default=None, alias="@baseType", description=fd["@baseType"]
    )
    schema_location: AnyUrl | None = Field(
        default=None, alias="@schemaLocation", description=fd["@schemaLocation"]
    )
    type: str | None = Field(
        default=None, alias="@type", description=fd["@type"]
    )
    characteristic_relationship: list[CharacteristicRelationship] | None = (
        Field(
            default=None,
            alias="characteristicRelationship",
            description=fd["characteristicRelationship"],
        )
    )
    id: str | None = Field(
        default_factory=lambda: str(uuid.uuid4()), description=fd["id"]
    )
    name: str = Field(description=fd["name"])
    value: types.Any = Field(description=fd["value"])
    value_type: str | None = Field(
        default=None, alias="valueType", description=fd["valueType"]
    )

import uuid

from pydantic import BaseModel, Field, AnyUrl

from schemas.characteristic_specification_relationship import (
    CharacteristicSpecificationRelationship,
)
from schemas.characteristic_value_specification import (
    CharacteristicValueSpecification,
)
from schemas.load_field_description import field_description
from schemas.time_period import TimePeriod

fd = field_description["CharacteristicSpecification"]


class CharacteristicSpecification(BaseModel):
    """
    This class defines a characteristic specification.
    """

    value_schema_location: str | None = Field(
        default=None,
        alias="@valueSchemaLocation",
        description=fd["@valueSchemaLocation"],
    )
    configurable: bool | None = Field(
        default=None, description=fd["configurable"]
    )
    description: str | None = Field(default=None, description=fd["description"])
    extensible: bool | None = Field(default=None, description=fd["extensible"])
    id: str | None = Field(
        default_factory=lambda: str(uuid.uuid4()), description=fd["id"]
    )
    is_unique: bool | None = Field(
        default=None, alias="isUnique", description=fd["isUnique"]
    )
    max_cardinality: int | None = Field(
        default=None, alias="maxCardinality", description=fd["maxCardinality"]
    )
    min_cardinality: int | None = Field(
        default=None, alias="minCardinality", description=fd["minCardinality"]
    )
    name: str | None = Field(default=None, description=fd["name"])
    regex: str | None = Field(default=None, description=fd["regex"])
    value_type: str | None = Field(
        default=None, alias="valueType", description=fd["valueType"]
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
    char_spec_relationship: (
        list[CharacteristicSpecificationRelationship] | None
    ) = Field(
        default=None,
        alias="charSpecRelationship",
        description=fd["charSpecRelationship"],
    )
    characteristic_value_specification: (
        list[CharacteristicValueSpecification] | None
    ) = Field(
        default=None,
        alias="characteristicValueSpecification",
        description=fd["characteristicValueSpecification"],
    )
    valid_for: TimePeriod | None = Field(
        default=None, alias="validFor", description=fd["validFor"]
    )

from pydantic import BaseModel, Field, AnyUrl

from schemas.load_field_description import field_description
from schemas.time_period import TimePeriod

fd = field_description["CharacteristicSpecificationRelationship"]


class CharacteristicSpecificationRelationship(BaseModel):
    """
    An aggregation, migration, substitution, dependency or exclusivity relationship between/among Characteristic
    specifications. The specification characteristic is embedded within the specification whose ID and href are in this
    entity, and identified by its ID.
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
    characteristic_specification_id: str | None = Field(
        default=None,
        alias="characteristicSpecificationId",
        description=fd["characteristicSpecificationId"],
    )
    name: str | None = Field(default=None, description=fd["name"])
    parent_specification_href: AnyUrl | None = Field(
        default=None,
        alias="parentSpecificationHref",
        description=fd["parentSpecificationHref"],
    )
    parent_specification_id: str | None = Field(
        default=None,
        alias="parentSpecificationId",
        description=fd["parentSpecificationId"],
    )
    relationship_type: str = Field(
        alias="relationshipType", description=fd["relationshipType"]
    )
    valid_for: TimePeriod = Field(alias="validFor", description=fd["validFor"])

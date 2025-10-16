from pydantic import BaseModel, Field, AnyUrl

from schemas.association_specification_ref import AssociationSpecificationRef
from schemas.load_field_description import field_description
from schemas.time_period import TimePeriod

fd = field_description["EntitySpecificationRelationship"]


class EntitySpecificationRelationship(BaseModel):
    """
    A migration, substitution, dependency, or exclusivity relationship between/among entity specifications.
    """

    referred_type: str | None = Field(
        default=None, alias="@referredType", description=fd["@referredType"]
    )
    name: str | None = Field(default=None, description=fd["name"])
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
    association_spec: AssociationSpecificationRef | None = Field(
        default=None, alias="associationSpec", description=fd["associationSpec"]
    )
    relationship_type: str = Field(
        alias="relationshipType", description=fd["relationshipType"]
    )
    role: str | None = Field(default=None, description=fd["role"])
    valid_for: TimePeriod | None = Field(
        default=None, alias="validFor", description=fd["validFor"]
    )

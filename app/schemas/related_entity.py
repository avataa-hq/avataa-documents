from pydantic import BaseModel, Field, AnyUrl

from schemas.load_field_description import field_description

fd = field_description["RelatedEntity"]


class RelatedEntity(BaseModel):
    """
    A reference to an entity, where the type of the entity is not known in advance.
    """

    referred_type: str = Field(
        alias="@referredType", description=fd["@referredType"]
    )
    name: str | None = Field(default=None, description=fd["name"])
    href: AnyUrl | None = Field(default=None, description=fd["href"])
    id: str = Field(description=fd["id"])
    base_type: str | None = Field(
        default=None, alias="@baseType", description=fd["@baseType"]
    )
    schema_location: AnyUrl | None = Field(
        default=None, alias="@schemaLocation", description=fd["@schemaLocation"]
    )
    type: str | None = Field(
        default=None, alias="@type", description=fd["@type"]
    )
    role: str = Field(description=fd["role"])

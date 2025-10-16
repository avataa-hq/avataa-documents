from pydantic import BaseModel, Field, AnyUrl

from schemas.load_field_description import field_description

fd = field_description["DocumentRef"]


class DocumentRef(BaseModel):
    referred_type: str | None = Field(
        default=None, alias="@referredType", description=fd["@referredType"]
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

from pydantic import BaseModel, Field

from schemas.load_field_description import field_description

fd = field_description["TargetEntitySchema"]


class TargetEntitySchema(BaseModel):
    """
    The reference object to the schema and type of target entity which is described by a specification.
    """

    schema_location: str = Field(
        alias="@schemaLocation", description=fd["@schemaLocation"]
    )
    type: str = Field(alias="@type", description=fd["@type"])

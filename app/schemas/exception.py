from pydantic import BaseModel, AnyUrl, Field

from schemas.load_field_description import field_description

fd = field_description["Exception"]


class ExceptionModel(BaseModel):
    """
    Used when an API throws an Error, typically with HTTP error response-code (3xx, 4xx, 5xx)
    """

    code: int = Field(description=fd["code"])
    reason: str = Field(description=fd["reason"])
    message: str | None = Field(default=None, description=fd["message"])
    status: int | None = Field(default=None, description=fd["status"])
    reference_error: str | None = Field(
        default=None, alias="referenceError", description=fd["referenceError"]
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

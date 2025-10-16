import uuid

from pydantic import BaseModel, Field, AnyUrl

from schemas.load_field_description import field_description
from schemas.quantity import Quantity
from schemas.time_period import TimePeriod

fd = field_description["AttachmentRefOrValue"]


class AttachmentRefOrValue(BaseModel):
    """
    An attachment by value or by reference. An attachment complements the description of an element,
    for example through a document, a video, a picture.
    """

    referred_type: str | None = Field(
        default=None, alias="@referredType", description=fd["@referredType"]
    )
    description: str | None = Field(default=None, description=fd["description"])
    href: AnyUrl | None = Field(default=None, description=fd["href"])
    id: str | None = Field(
        default_factory=lambda: str(uuid.uuid4()), description=fd["id"]
    )
    url: AnyUrl | None = Field(default=None, description=fd["url"])
    name: str | None = Field(description=fd["name"])
    base_type: str | None = Field(
        default=None, alias="@baseType", description=fd["@baseType"]
    )
    schema_location: AnyUrl | None = Field(
        default=None, alias="@schemaLocation", description=fd["@schemaLocation"]
    )
    type: str | None = Field(
        default=None, alias="@type", description=fd["@type"]
    )
    attachment_type: str | None = Field(
        default=None, alias="attachmentType", description=fd["attachmentType"]
    )
    content: str | None = Field(default=None, description=fd["content"])
    mime_type: str | None = Field(
        default=None, alias="mimeType", description=fd["mimeType"]
    )
    size: Quantity | None = Field(default=None, description=fd["size"])
    validFor: TimePeriod | None = Field(
        default=None, alias="validFor", description=fd["validFor"]
    )

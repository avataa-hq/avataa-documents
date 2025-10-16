import enum
from datetime import datetime

from pydantic import BaseModel, Field, AnyUrl

from schemas.document import Document
from schemas.document_specification import DocumentSpecification


class DocumentEventType(enum.Enum):
    CREATE = "DocumentCreateEvent"
    CHANGE = "DocumentChangeEvent"
    BATCH = "DocumentBatchEvent"
    DELETE = "DocumentDeleteEvent"


class DocumentSpecificationEventType(enum.Enum):
    CREATE = "DocumentSpecificationCreateEvent"
    CHANGE = "DocumentSpecificationAttributeValueChangeEvent"
    DELETE = "DocumentSpecificationDeleteEvent"


class SpecificEvent(BaseModel):
    document: Document | None = Field(default=None)
    document_specification: DocumentSpecification | None = Field(
        default=None, alias="documentSpecification"
    )


class Event(BaseModel):
    correlation_id: str | None = Field(default=None, alias="correlationId")
    description: str | None
    domain: str | None
    event_id: str = Field(alias="eventId")
    event_time: datetime = Field(alias="eventTime")
    event_type: DocumentEventType | DocumentSpecificationEventType = Field(
        alias="eventType"
    )
    field_path: str | None = Field(default=None, alias="fieldPath")
    href: AnyUrl | None
    id: str | None
    priority: str | None
    time_occurred: datetime | None = Field(default=None, alias="timeOccurred")
    title: str | None
    event: SpecificEvent

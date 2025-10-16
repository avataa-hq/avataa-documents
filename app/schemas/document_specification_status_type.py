import enum


class DocumentSpecificationStatusType(enum.Enum):
    CREATED = "created"
    REVIEWED = "reviewed"
    APPROVED = "approved"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    DELETED = "deleted"

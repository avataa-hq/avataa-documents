import enum


class RangeInterval(enum.Enum):
    OPEN = "open"
    CLOSED = "closed"
    CLOSED_BOTTOM = "closedBottom"
    CLOSED_TOP = "closedTop"

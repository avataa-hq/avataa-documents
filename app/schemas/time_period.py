from datetime import datetime

from pydantic import BaseModel, Field


class TimePeriod(BaseModel):
    end_datetime: datetime | None = Field(default=None, alias="endDateTime")
    start_datetime: datetime | None = Field(default=None, alias="startDateTime")

from pydantic import AnyUrl, BaseModel


class CreateListener(BaseModel):
    callback: AnyUrl


class Listener(BaseModel):
    id: str
    callback: AnyUrl
    query: str | None

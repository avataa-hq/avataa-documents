from fastapi import APIRouter

from schemas.event import Event

router = APIRouter()


@router.post("/client/listener", tags=["Listener"])
def publish_event_to_listener(event: Event):
    """
    Clears the communication endpoint address that was set by creating the Hub.
    Provides to a registered listener the description of the event that was raised. The /client/listener url is
    the callback url passed when registering the listener.
    """
    pass

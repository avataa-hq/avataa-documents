from fastapi import APIRouter, Path

from schemas.hub import Listener, CreateListener

router = APIRouter()


@router.post("/hub", tags=["Hub"], response_model=Listener)
def register_listener(listener: CreateListener):
    """
    Sets the communication endpoint address the service instance must use to deliver information about its health state,
    execution state, failures and metrics. Subsequent POST calls will be rejected by the service if it does not support
    multiple listeners. In this case DELETE /api/hub/{id} must be called before an endpoint can be created again.
    """
    pass


@router.delete("/hub/{id}", tags=["Hub"])
def unregister_listener(id_: str = Path(alias="id")):
    """
    Clears the communication endpoint address that was set by creating the Hub
    """
    pass

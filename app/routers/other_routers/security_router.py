import grpc
from fastapi import APIRouter

from database import db
from grpc_config.security_manager import (
    security_manager_pb2_grpc,
    security_manager_pb2,
)

from settings import INVENTORY_GRPC_PORT, INVENTORY_GRPC_HOST

router = APIRouter()


@router.get("/refresh_all_mo_permissions", tags=["Security"])
async def refresh_all_mo_permissions():
    db.permissions.delete_many({})

    async with grpc.aio.insecure_channel(
        f"{INVENTORY_GRPC_HOST}:{INVENTORY_GRPC_PORT}"
    ) as channel:
        stub = security_manager_pb2_grpc.SecurityManagerInformerStub(channel)
        msg = security_manager_pb2.RequestPermissionsForMO(get_permissions=True)
        grpc_response = stub.GetMOPermissions(msg)
        all_permissions = []
        async for grpc_chunk in grpc_response:
            all_permissions.append(grpc_chunk)

        for permission in all_permissions:
            for permission_instance in permission.mo_permissions:
                new_record = {
                    "read": permission_instance.read,
                    "update": permission_instance.update,
                    "create": permission_instance.create,
                    "delete": permission_instance.delete,
                    "admin": permission_instance.admin,
                    "parent_id": permission_instance.parent_id,
                    "root_permission_id": permission_instance.root_permission_id,
                    "permission_name": permission_instance.permission_name,
                    "permission": permission_instance.permission,
                }
                db.permissions.insert_one(new_record)

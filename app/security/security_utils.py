from database import db
from security.data.utils import role_prefix
from security.security_data_models import ClientRoles


def format_user_permissions(user_data: ClientRoles):
    permissions_to_search = [
        f"{user_data.name}.{role_prefix}{role}" for role in user_data.roles
    ]
    return permissions_to_search


def get_available_object_to_read_ids_by_user_data(user_data: ClientRoles):
    permissions_to_search = format_user_permissions(user_data=user_data)

    deny_receive_data = db.permissions.find(
        {"permission": {"$in": permissions_to_search}, "read": False}
    )
    if [instance for instance in deny_receive_data]:
        return []

    permit_instances = db.permissions.find(
        {"permission": {"$in": permissions_to_search}, "read": True}
    )
    available_object_ids = [
        str(permission["parent_id"]) for permission in permit_instances
    ]

    return available_object_ids


def get_available_object_to_create_ids_by_user_data(user_data: ClientRoles):
    permissions_to_search = format_user_permissions(user_data=user_data)

    deny_receive_data = db.permissions.find(
        {"permission": {"$in": permissions_to_search}, "create": False}
    )
    if [instance for instance in deny_receive_data]:
        return []

    permit_instances = db.permissions.find(
        {"permission": {"$in": permissions_to_search}, "create": True}
    )

    available_object_ids = [
        str(permission["id"]) for permission in permit_instances
    ]

    return available_object_ids


def get_available_object_to_update_ids_by_user_data(user_data: ClientRoles):
    permissions_to_search = format_user_permissions(user_data=user_data)

    deny_receive_data = db.permissions.find(
        {"permission": {"$in": permissions_to_search}, "update": False}
    )
    if [instance for instance in deny_receive_data]:
        return []

    permit_instances = db.permissions.find(
        {"permission": {"$in": permissions_to_search}, "update": True}
    )

    available_object_ids = [
        str(permission["id"]) for permission in permit_instances
    ]

    return available_object_ids


def get_available_object_to_delete_ids_by_user_data(user_data: ClientRoles):
    permissions_to_search = format_user_permissions(user_data=user_data)

    deny_receive_data = db.permissions.find(
        {"permission": {"$in": permissions_to_search}, "delete": False}
    )

    if [instance for instance in deny_receive_data]:
        return []

    permit_instances = db.permissions.find(
        {"permission": {"$in": permissions_to_search}, "delete": True}
    )

    available_object_ids = [
        str(permission["id"]) for permission in permit_instances
    ]

    return available_object_ids

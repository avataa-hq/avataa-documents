def add_to_query_permission_filter(
    filter_query: dict, available_object_ids_by_permission: list[int]
) -> dict:
    filter_query = dict(filter_query)

    available_object_ids_by_permission = [
        str(object_id) for object_id in available_object_ids_by_permission
    ]
    available_object_ids_by_permission.append(None)
    restriction = {
        "externalIdentifier.id": {"$in": available_object_ids_by_permission}
    }

    if filter_query:
        filter_query = {"$and": [filter_query, restriction]}
    else:
        filter_query = restriction

    return filter_query


class DocumentNotExists(Exception):
    pass

import functools
import json
import time
from enum import Enum
from typing import Union, Any

import requests
from fastapi import HTTPException
from google.protobuf import json_format

from database import db
from grpc_config.inventory_instances import inventory_instances_pb2
from grpc_config.security_manager.security_manager_pb2 import MOPermissions
from kafka.consumer.kafka_messages_adapter import (
    process_document_delete,
    process_security_message,
)
from schemas.document import ResponseDocument
from settings import (
    KAFKA_KEYCLOAK_SCOPES,
    KAFKA_KEYCLOAK_TOKEN_URL,
    KAFKA_KEYCLOAK_CLIENT_ID,
    KAFKA_KEYCLOAK_CLIENT_SECRET,
)


class SecurityEvent(Enum):
    CREATED = "security.created"
    UPDATED = "security.updated"
    DELETED = "security.deleted"


class ObjEventStatus(Enum):
    CREATED = "created"
    UPDATED = "updated"
    DELETED = "deleted"


def consumer_config(conf):
    if conf.get("sasl.mechanisms", "") == "OAUTHBEARER":
        conf["oauth_cb"] = functools.partial(_get_token_for_kafka_producer)
    return conf


def _get_token_for_kafka_producer(conf):
    """Get token from Keycloak for MS Inventory kafka_tools producer and returns it with
    expires time"""
    payload = {
        "grant_type": "client_credentials",
        "scope": str(KAFKA_KEYCLOAK_SCOPES),
    }

    attempt = 5
    while attempt > 0:
        try:
            resp = requests.post(
                KAFKA_KEYCLOAK_TOKEN_URL,
                auth=(KAFKA_KEYCLOAK_CLIENT_ID, KAFKA_KEYCLOAK_CLIENT_SECRET),
                data=payload,
                timeout=1,
            )
        except ConnectionError:
            time.sleep(1)
            attempt -= 1
        else:
            if resp.status_code == 200:
                break
            else:
                time.sleep(1)
                attempt -= 1
                continue
    else:
        raise HTTPException(
            status_code=503, detail="Token verification service unavailable"
        )

    token = resp.json()
    return token["access_token"], time.time() + float(token["expires_in"])


async def create_permission(objects: list[dict]):
    for obj in objects:
        db.permissions.insert_one(obj)


async def update_permission(objects: list[dict]):
    for obj in objects:
        db.document.replace_one({"id": obj["id"]}, obj)


async def delete_permission(objects: list[dict]):
    for obj in objects:
        db.collection.delete_one({"id": obj["id"]})


PROTO_TYPES_SERIALIZERS = {
    "Struct": lambda v: json_format.MessageToDict(v),
    "Timestamp": lambda v: json_format.MessageToDict(v),
}


def __msg_f_serializer(value: Any):
    """Returns serialized proto msg field value into python type"""
    serializer = PROTO_TYPES_SERIALIZERS.get(type(value).__name__)
    if serializer:
        return serializer(value)
    else:
        return value


def protobuf_kafka_msg_to_dict(
    msg: Union[
        inventory_instances_pb2.ListMO,
        inventory_instances_pb2.ListTMO,
        inventory_instances_pb2.ListTPRM,
        inventory_instances_pb2.ListPRM,
    ],
    including_default_value_fields: bool,
) -> dict:
    """Serialises protobuf.message.Message into python dict and returns it"""

    message_as_dict = dict()
    if including_default_value_fields is False:
        message_as_dict["objects"] = [
            {
                field.name: __msg_f_serializer(value)
                for field, value in item.ListFields()
            }
            for item in msg.objects
        ]
    else:
        message_as_dict["objects"] = [
            {
                field: __msg_f_serializer(getattr(item, field))
                for field in item.DESCRIPTOR.fields_by_name.keys()
            }
            for item in msg.objects
        ]
    return message_as_dict


def process_minio_changes(message):
    print("inside")
    value = json.loads(message.value())
    print(value)
    method = value["EventName"].split(":")[-1].lower()
    print(method)
    if method == "delete":
        print("inside 2")
        document_id = value["Key"].split("/")[1]
        print(document_id)
        process_document_delete(document_id=document_id)


async def process_security_changes(message, message_event: str):
    parser = MOPermissions()
    parser.ParseFromString(message.value())
    msg_dict = json_format.MessageToDict(
        parser,
        including_default_value_fields=False,
        preserving_proto_field_name=True,
    )
    if msg_dict:
        permissions = msg_dict["mo_permissions"]
    else:
        permissions = []
    await process_security_message(
        msg_event=message_event, permissions=permissions
    )


def process_object_changes(message, message_event: str):
    if message_event == ObjEventStatus.DELETED.value:
        value = inventory_instances_pb2.ListMO()
        value.ParseFromString(message.value())

        message_as_dict = protobuf_kafka_msg_to_dict(
            msg=value, including_default_value_fields=False
        )

        for deleted_object in message_as_dict["objects"]:
            query = {"externalIdentifier.id": str(deleted_object["id"])}
            linked_documents = db.document.find(query)
            linked_documents = [
                ResponseDocument(**doc) for doc in linked_documents
            ]
            for linked_document in linked_documents:
                process_document_delete(document_id=linked_document.id)


def message_is_empty(message, consumer):
    if message is None:
        consumer.commit(asynchronous=True)
        return True

    if getattr(message, "key", None) is None:
        consumer.commit(asynchronous=True)
        return True

    if message.key() is None:
        consumer.commit(asynchronous=True)
        return True

    return False

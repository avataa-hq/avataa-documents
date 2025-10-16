from database import db
from kafka.consumer import kafka_utils
from kafka.consumer.kafka_producer import (
    get_documents_kafka_producer_factory_method,
)
from schemas.document import Document
from utils.content_to_server import drop_document_data


def process_document_delete(document_id: str):
    document_data = db.document.find_one({"id": document_id})
    drop_document_data(
        document=document_data, base_url="", document_id=document_id
    )
    document = Document(**document_data)
    get_documents_kafka_producer_factory_method().send_deleted_attachments_by_doc(
        docs=[document]
    )


async def process_security_message(msg_event: str, permissions: list):
    if msg_event == kafka_utils.SecurityEvent.CREATED.value:
        await kafka_utils.create_permission(permissions)

    elif msg_event == kafka_utils.SecurityEvent.UPDATED.value:
        await kafka_utils.update_permission(permissions)

    elif msg_event == kafka_utils.SecurityEvent.DELETED.value:
        await kafka_utils.delete_permission(permissions)

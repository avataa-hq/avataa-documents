from abc import ABC, abstractmethod

import settings
from kafka import kafka_document_pb2
from schemas.document import Document
from settings import KAFKA_TURN_ON
from utils.kafka import send_to_kafka, DocumentsStatus


class KafkaProducerInterface(ABC):
    def __init__(self, kafka_topic):
        self.kafka_topic = kafka_topic

    @abstractmethod
    def send_created_attachments_by_mo_ids(self, mo_ids: list[int]):
        raise NotImplementedError()

    @abstractmethod
    def send_created_attachments_by_doc(self, docs: list[Document]):
        raise NotImplementedError()

    @abstractmethod
    def send_deleted_attachments_by_mo_ids(self, mo_ids: list[int]):
        raise NotImplementedError()

    @abstractmethod
    def send_deleted_attachments_by_doc(self, docs: list[Document]):
        raise NotImplementedError()


class DocumentsKafkaProducer(KafkaProducerInterface):
    @staticmethod
    def _collect_mo_ids(docs: list[Document]) -> list[int]:
        mo_ids = []
        for doc in docs:
            if not doc.external_identifier:
                continue
            attachment_count = len(doc.attachment)
            doc_mo_ids = [
                int(i.id) for i in doc.external_identifier if i.id.isdigit()
            ]
            for loop_index in range(attachment_count):
                mo_ids.extend(doc_mo_ids)
        return mo_ids

    def send_created_attachments_by_mo_ids(self, mo_ids: list[int]):
        if not mo_ids:
            return
        msg = kafka_document_pb2.Document(mo_id=mo_ids)
        send_to_kafka(
            data=msg, topic=self.kafka_topic, key=DocumentsStatus.CREATED.value
        )

    def send_created_attachments_by_doc(self, docs: list[Document]):
        mo_ids = DocumentsKafkaProducer._collect_mo_ids(docs=docs)
        self.send_created_attachments_by_mo_ids(mo_ids=mo_ids)

    def send_deleted_attachments_by_mo_ids(self, mo_ids: list[int]):
        if not mo_ids:
            return
        msg = kafka_document_pb2.Document(mo_id=mo_ids)
        send_to_kafka(
            data=msg, topic=self.kafka_topic, key=DocumentsStatus.DELETED.value
        )

    def send_deleted_attachments_by_doc(self, docs: list[Document]):
        mo_ids = DocumentsKafkaProducer._collect_mo_ids(docs=docs)
        self.send_deleted_attachments_by_mo_ids(mo_ids=mo_ids)


class DisabledDocumentsKafkaProducer(KafkaProducerInterface):
    def send_created_attachments_by_mo_ids(self, mo_ids: list[int]):
        print("send_created_attachments_by_mo_ids", mo_ids)
        pass

    def send_created_attachments_by_doc(self, docs: list[Document]):
        print("send_created_attachments_by_doc", len(docs))
        pass

    def send_deleted_attachments_by_mo_ids(self, mo_ids: list[int]):
        print("send_deleted_attachments_by_mo_ids", mo_ids)
        pass

    def send_deleted_attachments_by_doc(self, docs: list[Document]):
        print("send_deleted_attachments_by_doc", len(docs))
        pass


_instance = None


def get_documents_kafka_producer_factory_method():
    global _instance
    if not _instance:
        if KAFKA_TURN_ON:
            _instance = DocumentsKafkaProducer(
                kafka_topic=settings.KAFKA_PRODUCER_TOPIC
            )
        else:
            return DisabledDocumentsKafkaProducer(
                kafka_topic=settings.KAFKA_PRODUCER_TOPIC
            )
    print(_instance)
    return _instance

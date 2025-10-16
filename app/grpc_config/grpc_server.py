"""Async gRPC server"""

import asyncio
import logging

import grpc

from database import db
from .documents.proto import documents_pb2_grpc, documents_pb2


class DocumentInformer(documents_pb2_grpc.DocumentInformerServicer):
    async def GetObjectDocumentCount(
        self,
        request: documents_pb2.RequestGetObjectDocumentCount,
        context: grpc.aio.ServicerContext,
    ) -> documents_pb2.ResponseGetObjectDocumentCount:
        result = db.document.find(
            {"externalIdentifier.id": {"$exists": True}, "status": "created"}
        )
        documents = list(result)
        count_of_all_documents = len(documents)
        step = 10000

        for start in range(0, count_of_all_documents, step):
            end = min(start + step, count_of_all_documents)
            object_and_document_count = {}

            for document in documents[start:end]:
                object_id = document.get("externalIdentifier", [{}])[0].get(
                    "id"
                )
                if object_id is not None:
                    object_and_document_count[int(object_id)] = (
                        object_and_document_count.get(int(object_id), 0) + 1
                    )

            yield documents_pb2.ResponseGetObjectDocumentCount(
                object_and_documents=object_and_document_count
            )


async def start_grpc_serve() -> None:
    server = grpc.aio.server()
    documents_pb2_grpc.add_DocumentInformerServicer_to_server(
        DocumentInformer(), server
    )

    listen_addr = "[::]:50051"
    server.add_insecure_port(listen_addr)
    logging.info("Starting server on %s", listen_addr)
    await server.start()
    print("START GRPC")
    await server.wait_for_termination()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(start_grpc_serve())

import asyncio
import logging
import grpc
from google.protobuf import json_format
from grpc.aio import Channel
from documents.proto import documents_pb2_grpc, documents_pb2


async def get_object_and_document_count(channel: Channel) -> None:
    stub = documents_pb2_grpc.DocumentInformerStub(channel)
    message_as_dict = {}
    msg = documents_pb2.RequestGetObjectDocumentCount(check=True)
    response_async_generator = stub.GetObjectDocumentCount(msg)
    async for item in response_async_generator:
        message_as_dict = json_format.MessageToDict(
            item,
            including_default_value_fields=True,
            preserving_proto_field_name=True,
        )
    return message_as_dict


async def main():
    async with grpc.aio.insecure_channel("localhost:50051") as channel:
        await get_object_and_document_count(channel)


if __name__ == "__main__":
    logging.basicConfig()
    asyncio.run(main())

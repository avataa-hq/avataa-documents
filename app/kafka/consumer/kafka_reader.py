import asyncio
import functools

from confluent_kafka import Consumer

from settings import KAFKA_CONSUMER_CONNECT_CONFIG, KAFKA_SUBSCRIBE_TOPICS
from .kafka_utils import (
    consumer_config,
    process_minio_changes,
    process_security_changes,
    process_object_changes,
    message_is_empty,
)


async def read_kafka_topics():
    consumer = Consumer(consumer_config(KAFKA_CONSUMER_CONNECT_CONFIG))

    def assign(*args):
        print("successful subscription to the topic")
        print(KAFKA_SUBSCRIBE_TOPICS)

    consumer.subscribe(KAFKA_SUBSCRIBE_TOPICS, on_assign=assign)
    while True:
        loop = asyncio.get_running_loop()
        poll = functools.partial(consumer.poll, 1.0)
        kafka_message = await loop.run_in_executor(executor=None, func=poll)

        if message_is_empty(message=kafka_message, consumer=consumer):
            continue

        else:
            try:
                message_key = kafka_message.key().decode("utf-8")
                if "documents/" in message_key:
                    process_minio_changes(message=kafka_message)

                else:
                    message_class, message_event = message_key.split(":")

                    match message_class:
                        case "MOPermission":
                            await process_security_changes(
                                message=kafka_message,
                                message_event=message_event,
                            )

                        case "MO":
                            process_object_changes(
                                message=kafka_message,
                                message_event=message_event,
                            )

            except Exception as e:
                print(e)
            finally:
                consumer.commit(asynchronous=True)

    consumer.close()

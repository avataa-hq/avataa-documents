import asyncio

from kafka.consumer.kafka_reader import read_kafka_topics
from settings import KAFKA_TURN_ON

if __name__ == "__main__":
    if KAFKA_TURN_ON:
        asyncio.run(read_kafka_topics())

import functools
import time
from enum import Enum

import requests
import settings

from kafka import kafka_document_pb2
from confluent_kafka import Producer
from fastapi import HTTPException


class DocumentsStatus(Enum):
    CREATED = "CREATED"
    DELETED = "DELETED"


def send_to_kafka(data: kafka_document_pb2.Document, topic, key):
    prod_config = producer_config()
    producer = Producer(prod_config)
    producer.produce(
        topic=topic,
        key=key,
        value=data.SerializeToString(),
        on_delivery=delivery_report,
    )
    producer.flush()


def producer_config():
    if not settings.KAFKA_SECURED:
        return settings.KAFKA_PRODUCER_CONNECT_CONFIG

    config_dict = dict()
    config_dict.update(settings.KAFKA_PRODUCER_CONNECT_CONFIG)
    config_dict["oauth_cb"] = functools.partial(_get_token_for_kafka_producer)
    return config_dict


def _get_token_for_kafka_producer(conf):
    """Get token from Keycloak for MS Inventory kafka_tools producer and returns it with
    expires time"""
    payload = {
        "grant_type": "client_credentials",
        "scope": str(settings.KAFKA_KEYCLOAK_SCOPES),
    }

    attempt = 5
    while attempt > 0:
        try:
            resp = requests.post(
                settings.KAFKA_KEYCLOAK_TOKEN_URL,
                auth=(
                    settings.KAFKA_KEYCLOAK_CLIENT_ID,
                    settings.KAFKA_KEYCLOAK_CLIENT_SECRET,
                ),
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


def delivery_report(err, msg):
    """
    Reports the failure or success of a message delivery.
    Args:
        err (KafkaError): The error that occurred on None on success.
        msg (Message): The message that was produced or failed.
    """

    if err is not None:
        print("Delivery failed for User record {}: {}".format(msg.key(), err))
        return
    print(
        "User record {} successfully produced to {} [{}] at offset {}".format(
            msg.key(), msg.topic(), msg.partition(), msg.offset()
        )
    )

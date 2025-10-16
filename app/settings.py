import os


# URL = os.environ.get('URL', 'http://127.0.0.1:8101')
MINIO_URL = os.environ.get("MINIO_URL", "127.0.0.1:9000")
MINIO_USER = os.environ.get("MINIO_USER", "MINIO_ADMIN_USER")
MINIO_PASSWORD = os.environ.get("MINIO_PASSWORD", "MINIO_ADMIN_PASSWORD")
MINIO_BUCKET = os.environ.get("MINIO_BUCKET", "ms-document")
MINIO_SECURE = os.environ.get("MINIO_SECURE", "False").upper() in (
    "TRUE",
    "Y",
    "YES",
    "1",
)

MONGO_URL = os.environ.get("MONGO_URL", "127.0.0.1")
MONGO_PORT = os.environ.get("MONGO_PORT", "27017")
MONGO_USER = os.environ.get("MONGO_USER", "mongoadmin")
MONGO_PASSWORD = os.environ.get("MONGO_PASSWORD", "secret")
MONGO_DATABASE = os.environ.get("MONGO_DATABASE", "ms-document")

DEBUG = os.environ.get("DEBUG", "False").upper() in ("TRUE", "Y", "YES", "1")


ROOT_PREFIX = os.environ.get("ROOT_PREFIX", "/api/documents")
API_VERSION = os.environ.get("API_VERSION", "1")
PREFIX = ROOT_PREFIX.rstrip("/") + f"/v{API_VERSION}"

KAFKA_TURN_ON = str(os.environ.get("KAFKA_TURN_ON", True)).upper() in (
    "TRUE",
    "Y",
    "YES",
    "1",
)
KAFKA_URL = os.environ.get("KAFKA_URL", "localhost")

KAFKA_KEYCLOAK_SCOPES = os.environ.get("KAFKA_KEYCLOAK_SCOPES", "profile")
KAFKA_KEYCLOAK_CLIENT_ID = os.environ.get("KAFKA_KEYCLOAK_CLIENT_ID", "kafka")
KAFKA_KEYCLOAK_CLIENT_SECRET = os.environ.get(
    "KAFKA_KEYCLOAK_CLIENT_SECRET", "secret"
)
KAFKA_KEYCLOAK_TOKEN_URL = os.environ.get(
    "KAFKA_KEYCLOAK_TOKEN_URL", "token_url"
)
KAFKA_SECURED = str(os.environ.get("KAFKA_SECURED", True)).upper() in (
    "TRUE",
    "Y",
    "YES",
    "1",
)

KAFKA_PRODUCER_TOPIC = os.environ.get(
    "KAFKA_PRODUCER_TOPIC", "documents.changes"
)
KAFKA_PRODUCER_CONNECT_CONFIG = {"bootstrap.servers": KAFKA_URL}

KAFKA_CONSUMER_GROUP_ID = os.environ.get("KAFKA_CONSUMER_GROUP_ID", "Documents")
KAFKA_CONSUMER_OFFSET = os.environ.get("KAFKA_CONSUMER_OFFSET", "latest")
KAFKA_SECURITY_TOPIC = os.environ.get(
    "KAFKA_SECURITY_TOPIC", "inventory.security"
)
KAFKA_INVENTORY_CHANGES_TOPIC = os.environ.get(
    "KAFKA_INVENTORY_CHANGES_TOPIC", "inventory.changes"
)
KAFKA_MINIO_CHANGES_TOPIC = os.environ.get(
    "KAFKA_MINIO_CHANGES_TOPIC", "minio.changes"
)

KAFKA_SUBSCRIBE_TOPICS = f"{KAFKA_MINIO_CHANGES_TOPIC},{KAFKA_SECURITY_TOPIC},{KAFKA_INVENTORY_CHANGES_TOPIC}"

KAFKA_SUBSCRIBE_TOPICS = KAFKA_SUBSCRIBE_TOPICS.split(",")

KAFKA_CONSUMER_CONNECT_CONFIG = {
    "bootstrap.servers": KAFKA_URL,
    "group.id": KAFKA_CONSUMER_GROUP_ID,
    "auto.offset.reset": KAFKA_CONSUMER_OFFSET,
    "enable.auto.commit": False,
}

if KAFKA_SECURED:
    SECURED_SETTINGS = {
        "security.protocol": "sasl_plaintext",
        "sasl.mechanisms": "OAUTHBEARER",
    }
    KAFKA_PRODUCER_CONNECT_CONFIG.update(SECURED_SETTINGS)
    KAFKA_CONSUMER_CONNECT_CONFIG.update(SECURED_SETTINGS)

INVENTORY_OBJECT_PREFIX = os.environ.get(
    "INVENTORY_OBJECT_PREFIX",
    "https://avataa.dev/api/inventory/v1/inventory/object/",
)

# DOCUMENTATION
DOCS_ENABLED = os.environ.get("DOCS_ENABLED", "True").upper() in (
    "TRUE",
    "Y",
    "YES",
    "1",
)
DOCS_CUSTOM_ENABLED = os.environ.get(
    "DOCS_CUSTOM_ENABLED", "False"
).upper() in ("TRUE", "Y", "YES", "1")
SWAGGER_JS_URL = os.environ.get("DOCS_SWAGGER_JS_URL", None)
SWAGGER_CSS_URL = os.environ.get("DOCS_SWAGGER_CSS_URL", None)
REDOC_JS_URL = os.environ.get("DOCS_REDOC_JS_URL", None)

INVENTORY_GRPC_HOST = os.environ.get("INVENTORY_GRPC_HOST", "localhost")
INVENTORY_GRPC_PORT = os.environ.get("INVENTORY_GRPC_PORT", "50051")

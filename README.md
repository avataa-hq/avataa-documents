# Documents

## Environment variables

```toml
DEBUG=<True/False>
DOCS_CUSTOM_ENABLED=<True/False>
DOCS_REDOC_JS_URL=<redoc_js_url>
DOCS_SWAGGER_CSS_URL=<swagger_css_url>
DOCS_SWAGGER_JS_URL=<swagger_js_url>
INVENTORY_GRPC_HOST=<inventory_host>
INVENTORY_GRPC_PORT=<inventory_grpc_port>
KAFKA_CONSUMER_GROUP_ID=Documents
KAFKA_CONSUMER_OFFSET=latest
KAFKA_KEYCLOAK_CLIENT_ID=<kafka_client>
KAFKA_KEYCLOAK_CLIENT_SECRET=<kafka_client_secret>
KAFKA_KEYCLOAK_SCOPES=profile
KAFKA_KEYCLOAK_TOKEN_URL=http://keycloak:8080/realms/avataa/protocol/openid-connect/token
KAFKA_MINIO_CHANGES_TOPIC=minio.changes
KAFKA_PRODUCER_TOPIC=documents.changes
KAFKA_SECURED=<True/False>
KAFKA_SECURITY_TOPIC=inventory.security
KAFKA_TURN_ON=<True/False>
KAFKA_URL=<kafka_host>:<kafka_port>
KEYCLOAK_HOST=<keycloak_host>
KEYCLOAK_PORT=<keycloak_port>
KEYCLOAK_PROTOCOL=<keycloak_protocol>
KEYCLOAK_REALM=avataa
KEYCLOAK_REDIRECT_HOST=<keycloak_external_host>
KEYCLOAK_REDIRECT_PORT=<keycloak_external_port>
KEYCLOAK_REDIRECT_PROTOCOL=<keycloak_external_protocol>
MINIO_BUCKET=<minio_documents_bucket>
MINIO_PASSWORD=<minio_documents_password>
MINIO_SECURE=<True/False>
MINIO_URL=<minio_api_host>
MINIO_USER=<minio_documents_user>
MONGO_DATABASE=<mongo_documents_db_name>
MONGO_PASSWORD=<mongo_documents_password>
MONGO_PORT=<mongo_documents_port>
MONGO_URL=<mongo_documents_host>
MONGO_USER=<mongo_documents_user>
OPA_HOST=<opa_host>
OPA_POLICY=main
OPA_PORT=<opa_port>
OPA_PROTOCOL=<opa_protocol>
SECURITY_TYPE=<security_type>
UVICORN_WORKERS=<uvicorn_workers_number>
```

## Explanation

### Compose

- `REGISTRY_URL` - Docker regitry URL, e.g. `harbor.domain.com`
- `PLATFORM_PROJECT_NAME` - Docker regitry project Docker image can be downloaded from, e.g. `avataa`
Export Compliance

This Software, including any source code, technology, and technical data, is distributed under the Apache License, Version 2.0.

Users of this Software are solely responsible for compliance with all applicable national and international laws, regulations, and restrictions pertaining to export, re-export, or import. This includes, but is not limited to, the U.S. Export Administration Regulations (EAR) and restrictions concerning embargoed countries and restricted party lists.

By downloading, accessing, or using this Software, you affirm that:

1.  You are not located in a country that is subject to a U.S. government embargo or has been designated by the U.S. government as a "terrorist supporting" country.
2.  You are not listed on any U.S. government list of prohibited or restricted parties (e.g., the Specially Designated Nationals List or the Denied Persons List).

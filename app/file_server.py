from minio import Minio
from minio.lifecycleconfig import (
    LifecycleConfig,
    Rule,
    Expiration,
    NoncurrentVersionExpiration,
)
from minio.sseconfig import SSEConfig, Rule as SseRule
from minio.versioningconfig import VersioningConfig
from minio.commonconfig import ENABLED

import settings


class MinioClient:
    def __init__(
        self, url: str, user: str, password: str, secure: bool = False
    ):
        self._url = url
        self._user = user
        self._password = password
        self._secure = secure
        self._minio_client = None

    def __call__(self):
        if self._minio_client is None:
            self.init_bucket()
        return self._minio_client

    def init_bucket(self):
        self._minio_client = Minio(
            self._url, self._user, self._password, secure=self._secure
        )
        client = self._minio_client
        if not client.bucket_exists(settings.MINIO_BUCKET):
            client.make_bucket(settings.MINIO_BUCKET)
            client.set_bucket_versioning(
                settings.MINIO_BUCKET, VersioningConfig(ENABLED)
            )
            client.set_bucket_encryption(
                settings.MINIO_BUCKET, SSEConfig(SseRule.new_sse_s3_rule())
            )

            lifecycle_config = LifecycleConfig(
                [
                    Rule(
                        ENABLED,
                        rule_id="noncurrent version delete",
                        noncurrent_version_expiration=NoncurrentVersionExpiration(
                            noncurrent_days=366
                        ),
                    ),
                    Rule(
                        ENABLED,
                        rule_id="removing files with delete marker",
                        expiration=Expiration(
                            days=366, expired_object_delete_marker=True
                        ),
                    ),
                ]
            )
            client.set_bucket_lifecycle(settings.MINIO_BUCKET, lifecycle_config)


minio_client = MinioClient(
    url=settings.MINIO_URL,
    user=settings.MINIO_USER,
    password=settings.MINIO_PASSWORD,
    secure=settings.MINIO_SECURE,
)

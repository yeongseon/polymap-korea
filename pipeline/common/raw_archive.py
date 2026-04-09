from __future__ import annotations

from importlib import import_module
import json
from collections.abc import Mapping
from datetime import timezone
from typing import Any, Protocol, cast

from common.base_adapter import RawRecord


class S3ClientProtocol(Protocol):
    def list_buckets(self) -> dict[str, object]: ...

    def create_bucket(self, *, Bucket: str) -> object: ...

    def put_object(self, *, Bucket: str, Key: str, Body: bytes) -> object: ...


class RawArchive:
    def __init__(
        self,
        bucket_name: str,
        endpoint_url: str,
        access_key: str,
        secret_key: str,
        region_name: str = "us-east-1",
    ) -> None:
        self.bucket_name = bucket_name
        boto3_module = import_module("boto3")
        self.client = cast(S3ClientProtocol, boto3_module.client(
            "s3",
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region_name,
        ))

    def ensure_bucket(self) -> None:
        response = self.client.list_buckets()
        raw_buckets = cast(list[object], response.get("Buckets", []))
        buckets = {
            bucket["Name"]
            for bucket in raw_buckets
            if isinstance(bucket, dict) and isinstance(bucket.get("Name"), str)
        }
        if self.bucket_name not in buckets:
            self.client.create_bucket(Bucket=self.bucket_name)

    def archive_record(self, record: RawRecord) -> str:
        record.compute_hash()
        key = self._build_object_key(record)
        body = self._serialize_record(record)
        self.client.put_object(Bucket=self.bucket_name, Key=key, Body=body.encode("utf-8"))
        return key

    def _build_object_key(self, record: RawRecord) -> str:
        timestamp = record.fetched_at.astimezone(timezone.utc).strftime("%Y/%m/%d/%H%M%S")
        return f"{record.source_system}/{timestamp}-{record.response_hash or 'pending'}.json"

    def _serialize_record(self, record: RawRecord) -> str:
        payload: Mapping[str, Any] = {
            "source_system": record.source_system,
            "endpoint": record.endpoint,
            "request_params": record.request_params,
            "fetched_at": record.fetched_at.isoformat(),
            "http_status": record.http_status,
            "response_hash": record.response_hash,
            "license_note": record.license_note,
            "election_phase": record.election_phase,
            "public_expiry_at": (
                record.public_expiry_at.isoformat() if record.public_expiry_at is not None else None
            ),
            "data": record.data,
        }
        return json.dumps(payload, ensure_ascii=False, sort_keys=True)

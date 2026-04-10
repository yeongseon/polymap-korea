from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel

from polymap_api.deps import require_admin

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["admin"])


class EntityCatalogEntry(BaseModel):
    table: str
    description: str
    priority: str


class SnapshotPublishRequest(BaseModel):
    version: str
    schema_version: str
    generated_at: str
    entity_catalog: list[EntityCatalogEntry]
    entity_count: int
    publish_targets: list[str]


class SnapshotPublishResponse(BaseModel):
    status: str
    message: str


@router.post(
    "/publish/snapshot",
    response_model=SnapshotPublishResponse,
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(require_admin)],
)
async def publish_snapshot(payload: SnapshotPublishRequest) -> SnapshotPublishResponse:
    logger.info("Accepted snapshot publish request for version %s", payload.version)
    return SnapshotPublishResponse(
        status="accepted",
        message=f"Snapshot v{payload.version} accepted for processing",
    )

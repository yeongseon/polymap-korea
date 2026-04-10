from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel

from polymap_api.deps import require_admin

router = APIRouter(prefix="/admin", tags=["admin"])


class SnapshotPublishRequest(BaseModel):
    snapshot: dict[str, Any]


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
    return SnapshotPublishResponse(
        status="accepted",
        message=f"Snapshot v{payload.snapshot.get('version', 'unknown')} accepted for processing",
    )

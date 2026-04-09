# ruff: noqa: B008,TC002,TC003
from __future__ import annotations

import asyncio
import json
from collections.abc import AsyncIterator
from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from starlette.requests import Request

from polymap_api.deps import get_db
from polymap_api.models import Election, Race

router = APIRouter(tags=["sse"])


@router.get("/elections/{election_id}/live")
async def stream_election_live_updates(
    election_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> StreamingResponse:
    election = await db.get(Election, election_id)
    if election is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Election not found")

    async def event_stream() -> AsyncIterator[str]:
        next_heartbeat_at = 15.0
        next_update_at = 0.0
        elapsed = 0.0
        try:
            while not await request.is_disconnected():
                if elapsed >= next_update_at:
                    races = list(
                        await db.scalars(
                            select(Race)
                            .options(selectinload(Race.candidacies))
                            .where(Race.election_id == election_id)
                        )
                    )
                    payload = {
                        "election_id": str(election.id),
                        "generated_at": datetime.now(timezone.utc).isoformat(),
                        "race_count": len(races),
                        "candidacy_count": sum(len(race.candidacies) for race in races),
                    }
                    yield f"event: election_update\ndata: {json.dumps(payload)}\n\n"
                    next_update_at += 30.0

                if elapsed >= next_heartbeat_at:
                    yield ": heartbeat\n\n"
                    next_heartbeat_at += 15.0

                await asyncio.sleep(1)
                elapsed += 1.0
        except asyncio.CancelledError:
            return

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )

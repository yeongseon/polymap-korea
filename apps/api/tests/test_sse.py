# ruff: noqa: TC002,TC003
from __future__ import annotations

from collections.abc import AsyncIterator
from typing import cast
from uuid import UUID

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from polymap_api.routers.sse import stream_election_live_updates


class _StaticDisconnectRequest(Request):
    def __init__(self) -> None:
        async def receive() -> dict[str, object]:
            return {"type": "http.request", "body": b"", "more_body": False}

        super().__init__({"type": "http", "method": "GET", "path": "/", "headers": []}, receive)
        self._calls = 0

    async def is_disconnected(self) -> bool:
        self._calls += 1
        return self._calls > 1


@pytest.mark.asyncio
async def test_stream_election_live_updates_emits_event(
    db_session: AsyncSession,
    seeded_db: dict[str, object],
) -> None:
    election_id = cast("UUID", seeded_db["election"])
    response = await stream_election_live_updates(
        election_id=election_id,
        request=_StaticDisconnectRequest(),
        db=db_session,
    )

    assert response.media_type == "text/event-stream"
    assert response.headers["cache-control"] == "no-cache"
    assert response.headers["x-accel-buffering"] == "no"

    first_chunk = await anext(cast("AsyncIterator[str]", response.body_iterator))

    assert "event: election_update" in first_chunk
    assert f'"election_id": "{election_id}"' in first_chunk

# ruff: noqa: TC002,E501
from __future__ import annotations

import uuid

import pytest
from httpx import AsyncClient

from polymap_api.models import Promise


@pytest.mark.asyncio
async def test_compare_candidacies_groups_promises_by_issue(
    client: AsyncClient,
    db_session,
    seeded_db: dict[str, object],
) -> None:
    db_session.add_all(
        [
            Promise(
                id=uuid.uuid4(),
                candidacy_id=seeded_db["candidacy_two"],
                title="Bus rapid transit 확대",
                body="버스 노선과 BRT를 확대합니다.",
                issue_id=seeded_db["issue"],
                source_doc_id=seeded_db["source_doc"],
                sort_order=1,
            ),
            Promise(
                id=uuid.uuid4(),
                candidacy_id=seeded_db["candidacy"],
                title="열린 행정 플랫폼 구축",
                body="민원과 예산 공개를 강화합니다.",
                source_doc_id=seeded_db["source_doc"],
                sort_order=2,
            ),
        ]
    )
    await db_session.commit()

    response = await client.post(
        "/api/v1/compare",
        json={"candidacy_ids": [str(seeded_db["candidacy"]), str(seeded_db["candidacy_two"])]},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["candidacy_ids"] == [str(seeded_db["candidacy"]), str(seeded_db["candidacy_two"])]
    assert data["by_issue"][0]["issue_id"] == str(seeded_db["issue"])
    assert data["by_issue"][0]["issue_name"] == "Transit"
    assert data["by_issue"][0]["candidates"][0]["person_name"] == "홍길동"
    assert data["by_issue"][0]["candidates"][0]["party_name"] == "미래당"
    assert data["by_issue"][0]["candidates"][0]["promises"][0]["title"] == "Transit expansion"
    assert data["by_issue"][0]["candidates"][1]["promises"][0]["title"] == "Bus rapid transit 확대"
    assert data["by_issue"][1]["issue_id"] is None
    assert data["by_issue"][1]["candidates"][0]["promises"][0]["title"] == "열린 행정 플랫폼 구축"
    assert data["by_issue"][1]["candidates"][1]["promises"] == []


@pytest.mark.asyncio
async def test_candidacy_promises_include_metadata_field(
    client: AsyncClient,
    db_session,
    seeded_db: dict[str, object],
) -> None:
    db_session.add(
        Promise(
            id=uuid.uuid4(),
            candidacy_id=seeded_db["candidacy"],
            title="맞춤형 공약 분류",
            body="키워드 기반 분류 정보를 제공합니다.",
            source_doc_id=seeded_db["source_doc"],
            sort_order=0,
            metadata={"issue_slugs": ["administration"]},
        )
    )
    await db_session.commit()

    response = await client.get(f"/api/v1/candidacies/{seeded_db['candidacy']}/promises")

    assert response.status_code == 200
    data = response.json()
    assert data[0]["metadata"] == {"issue_slugs": ["administration"]}


def test_promise_schema_accepts_metadata_key_on_input() -> None:
    """Verify that inbound payloads using 'metadata' (not 'metadata_') are accepted."""
    from polymap_api.schemas.promise import PromiseCreate

    payload = {
        "candidacy_id": "00000000-0000-0000-0000-000000000001",
        "title": "Test promise",
        "body": "Test body",
        "metadata": {"issue_slugs": ["economy-jobs"]},
    }
    obj = PromiseCreate.model_validate(payload)
    assert obj.metadata_ == {"issue_slugs": ["economy-jobs"]}
    dumped = obj.model_dump(by_alias=True)
    assert dumped["metadata"] == {"issue_slugs": ["economy-jobs"]}


def test_promise_schema_accepts_metadata_underscore_on_input() -> None:
    """Verify that inbound payloads using 'metadata_' are also accepted."""
    from polymap_api.schemas.promise import PromiseCreate

    payload = {
        "candidacy_id": "00000000-0000-0000-0000-000000000001",
        "title": "Test promise",
        "body": "Test body",
        "metadata_": {"issue_slugs": ["welfare-elderly"]},
    }
    obj = PromiseCreate.model_validate(payload)
    assert obj.metadata_ == {"issue_slugs": ["welfare-elderly"]}

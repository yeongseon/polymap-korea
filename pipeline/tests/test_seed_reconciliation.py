from __future__ import annotations

import asyncio
from unittest.mock import patch

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine

from taxonomy.seed import (
    _canonical_edges,
    _reconcile_relations,
    _seed_issues,
    issue_relation_table,
    issue_table,
    metadata,
)

TAXONOMY_V1 = [
    {
        "slug": "parent-a",
        "name": "Parent A",
        "children": [
            {"slug": "child-x", "name": "Child X"},
            {"slug": "child-y", "name": "Child Y"},
        ],
    },
    {
        "slug": "parent-b",
        "name": "Parent B",
        "children": [],
    },
]

TAXONOMY_V2_REPARENTED = [
    {
        "slug": "parent-a",
        "name": "Parent A",
        "children": [
            {"slug": "child-y", "name": "Child Y"},
        ],
    },
    {
        "slug": "parent-b",
        "name": "Parent B",
        "children": [
            {"slug": "child-x", "name": "Child X Moved"},
        ],
    },
]

TAXONOMY_V3_DELETED = [
    {
        "slug": "parent-a",
        "name": "Parent A",
        "children": [
            {"slug": "child-y", "name": "Child Y"},
        ],
    },
    {
        "slug": "parent-b",
        "name": "Parent B",
        "children": [],
    },
]


async def _run_seed_cycle(engine, taxonomy):
    with patch("taxonomy.seed._load_taxonomy", return_value=taxonomy):
        async with engine.begin() as conn:
            issue_ids = await _seed_issues(conn)
            canonical = _canonical_edges(taxonomy, issue_ids)
            await _reconcile_relations(conn, canonical)
    return issue_ids


async def _get_relation_edges(engine):
    async with engine.connect() as conn:
        rows = await conn.execute(
            select(
                issue_relation_table.c.source_issue_id,
                issue_relation_table.c.target_issue_id,
                issue_relation_table.c.relation_type,
            )
        )
        return {(r.source_issue_id, r.target_issue_id, str(r.relation_type)) for r in rows.all()}


async def _get_issue_slugs(engine):
    async with engine.connect() as conn:
        rows = await conn.execute(select(issue_table.c.slug))
        return {r.slug for r in rows.all()}


@pytest.mark.asyncio
async def test_reparenting_removes_old_relation_edges() -> None:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)

    ids_v1 = await _run_seed_cycle(engine, TAXONOMY_V1)

    edges_v1 = await _get_relation_edges(engine)
    parent_a_id = ids_v1["parent-a"]
    child_x_id = ids_v1["child-x"]
    child_y_id = ids_v1["child-y"]
    assert (child_x_id, parent_a_id, "broader") in edges_v1
    assert (parent_a_id, child_x_id, "narrower") in edges_v1
    assert (child_y_id, parent_a_id, "broader") in edges_v1
    assert len(edges_v1) == 4

    ids_v2 = await _run_seed_cycle(engine, TAXONOMY_V2_REPARENTED)

    edges_v2 = await _get_relation_edges(engine)
    parent_b_id = ids_v2["parent-b"]

    assert (child_x_id, parent_a_id, "broader") not in edges_v2
    assert (parent_a_id, child_x_id, "narrower") not in edges_v2

    assert (child_x_id, parent_b_id, "broader") in edges_v2
    assert (parent_b_id, child_x_id, "narrower") in edges_v2

    assert (child_y_id, parent_a_id, "broader") in edges_v2
    assert (parent_a_id, child_y_id, "narrower") in edges_v2

    assert len(edges_v2) == 4

    await engine.dispose()


@pytest.mark.asyncio
async def test_deleting_child_removes_issue_and_relations() -> None:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)

    await _run_seed_cycle(engine, TAXONOMY_V1)
    slugs_v1 = await _get_issue_slugs(engine)
    assert "child-x" in slugs_v1

    await _run_seed_cycle(engine, TAXONOMY_V3_DELETED)

    slugs_v3 = await _get_issue_slugs(engine)
    assert "child-x" not in slugs_v3
    assert "child-y" in slugs_v3
    assert "parent-a" in slugs_v3
    assert "parent-b" in slugs_v3

    edges_v3 = await _get_relation_edges(engine)
    assert len(edges_v3) == 2

    await engine.dispose()


@pytest.mark.asyncio
async def test_idempotent_seed_preserves_edge_count() -> None:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)

    await _run_seed_cycle(engine, TAXONOMY_V1)
    edges_first = await _get_relation_edges(engine)

    await _run_seed_cycle(engine, TAXONOMY_V1)
    edges_second = await _get_relation_edges(engine)

    assert edges_first == edges_second

    await engine.dispose()

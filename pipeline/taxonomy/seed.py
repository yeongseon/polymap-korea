from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime, Enum, ForeignKey, MetaData, String, Table, Text, Uuid, func, select
from sqlalchemy.ext.asyncio import AsyncConnection, create_async_engine

ROOT = Path(__file__).resolve().parents[2]
ONTOLOGY_SRC = ROOT / "packages" / "ontology" / "src"
if str(ONTOLOGY_SRC) not in sys.path:
    sys.path.insert(0, str(ONTOLOGY_SRC))

from polymap_ontology.enums import IssueRelationType

TAXONOMY_JSON = Path(__file__).resolve().parent / "taxonomy.json"


def _load_taxonomy() -> list[dict[str, object]]:
    with open(TAXONOMY_JSON, encoding="utf-8") as f:
        return json.load(f)


metadata = MetaData()
issue_table = Table(
    "issue",
    metadata,
    Column("id", Uuid(as_uuid=True), primary_key=True),
    Column("name", String(200), nullable=False),
    Column("slug", String(200), nullable=False),
    Column("description", Text, nullable=True),
    Column("parent_id", Uuid(as_uuid=True), ForeignKey("issue.id", ondelete="SET NULL"), nullable=True),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    Column("updated_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
)
issue_relation_table = Table(
    "issue_relation",
    metadata,
    Column("id", Uuid(as_uuid=True), primary_key=True),
    Column("source_issue_id", Uuid(as_uuid=True), ForeignKey("issue.id", ondelete="CASCADE"), nullable=False),
    Column("target_issue_id", Uuid(as_uuid=True), ForeignKey("issue.id", ondelete="CASCADE"), nullable=False),
    Column("relation_type", Enum(IssueRelationType, name="issue_relation_type_enum"), nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    Column("updated_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
)


async def _load_issue_ids(conn: AsyncConnection) -> dict[str, UUID]:
    rows = await conn.execute(select(issue_table.c.slug, issue_table.c.id))
    return {slug: issue_id for slug, issue_id in rows.all()}


async def _seed_issues(conn: AsyncConnection) -> dict[str, UUID]:
    taxonomy = _load_taxonomy()
    issue_ids = await _load_issue_ids(conn)

    for parent in taxonomy:
        parent_slug = str(parent["slug"])
        if parent_slug not in issue_ids:
            parent_id = uuid4()
            await conn.execute(
                issue_table.insert().values(
                    id=parent_id,
                    name=str(parent["name"]),
                    slug=parent_slug,
                    description=None,
                    parent_id=None,
                )
            )
            issue_ids[parent_slug] = parent_id

    for parent in taxonomy:
        parent_id = issue_ids[str(parent["slug"])]
        children = parent.get("children", [])
        assert isinstance(children, list)
        for child in children:
            child_slug = str(child["slug"])
            if child_slug in issue_ids:
                continue
            child_id = uuid4()
            await conn.execute(
                issue_table.insert().values(
                    id=child_id,
                    name=str(child["name"]),
                    slug=child_slug,
                    description=None,
                    parent_id=parent_id,
                )
            )
            issue_ids[child_slug] = child_id

    return issue_ids


async def seed_taxonomy() -> None:
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL is required")

    taxonomy = _load_taxonomy()
    engine = create_async_engine(database_url)
    try:
        async with engine.begin() as conn:
            issue_ids = await _seed_issues(conn)
            for parent in taxonomy:
                parent_id = issue_ids[str(parent["slug"])]
                children = parent.get("children", [])
                assert isinstance(children, list)
                for child in children:
                    child_id = issue_ids[str(child["slug"])]
                    await _ensure_relation(conn, child_id, parent_id, IssueRelationType.BROADER)
                    await _ensure_relation(conn, parent_id, child_id, IssueRelationType.NARROWER)
    finally:
        await engine.dispose()


async def _ensure_relation(
    conn: AsyncConnection,
    source_issue_id: UUID,
    target_issue_id: UUID,
    relation_type: IssueRelationType,
) -> None:
    existing = await conn.execute(
        select(issue_relation_table.c.id).where(
            issue_relation_table.c.source_issue_id == source_issue_id,
            issue_relation_table.c.target_issue_id == target_issue_id,
            issue_relation_table.c.relation_type == relation_type,
        )
    )
    if existing.scalar_one_or_none() is not None:
        return
    await conn.execute(
        issue_relation_table.insert().values(
            id=uuid4(),
            source_issue_id=source_issue_id,
            target_issue_id=target_issue_id,
            relation_type=relation_type,
        )
    )


def main() -> None:
    asyncio.run(seed_taxonomy())


if __name__ == "__main__":
    main()

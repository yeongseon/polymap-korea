from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

revision = "20260409_02"
down_revision = "20260409_01"
branch_labels = None
depends_on = None


def _has_table(inspector: sa.Inspector, table_name: str) -> bool:
    return table_name in inspector.get_table_names()


def _column_names(inspector: sa.Inspector, table_name: str) -> set[str]:
    return {column["name"] for column in inspector.get_columns(table_name)}


def _column_names_via_sql(bind: sa.Connection, table_name: str) -> set[str]:
    dialect = bind.dialect.name
    if dialect == "sqlite":
        rows = bind.execute(text(f"PRAGMA table_info({table_name})")).mappings()
        return {row["name"] for row in rows}
    rows = bind.execute(
        text(
            """
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = :table_name
            """
        ),
        {"table_name": table_name},
    ).mappings()
    return {row["column_name"] for row in rows}


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not _has_table(inspector, "election_window"):
        op.create_table(
            "election_window",
            sa.Column("election_id", sa.Uuid(), nullable=False),
            sa.Column("content_type", sa.String(length=100), nullable=False),
            sa.Column("blackout_start", sa.DateTime(timezone=True), nullable=False),
            sa.Column("blackout_end", sa.DateTime(timezone=True), nullable=False),
            sa.Column("id", sa.Uuid(), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
            sa.CheckConstraint("blackout_start < blackout_end", name=op.f("ck_election_window_window_bounds")),
            sa.ForeignKeyConstraint(["election_id"], ["election.id"], name=op.f("fk_election_window_election_id_election"), ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id", name=op.f("pk_election_window")),
        )
    else:
        election_window_columns = _column_names_via_sql(bind, "election_window")
        with op.batch_alter_table("election_window") as batch_op:
            if "content_type" not in election_window_columns:
                batch_op.add_column(sa.Column("content_type", sa.String(length=100), nullable=True))
            if "blackout_start" not in election_window_columns:
                batch_op.add_column(sa.Column("blackout_start", sa.DateTime(timezone=True), nullable=True))
            if "blackout_end" not in election_window_columns:
                batch_op.add_column(sa.Column("blackout_end", sa.DateTime(timezone=True), nullable=True))

        election_window_columns = _column_names_via_sql(bind, "election_window")
        if "phase" in election_window_columns and "content_type" in election_window_columns:
            bind.execute(text("UPDATE election_window SET content_type = phase WHERE content_type IS NULL"))
        if "starts_at" in election_window_columns and "blackout_start" in election_window_columns:
            bind.execute(text("UPDATE election_window SET blackout_start = starts_at WHERE blackout_start IS NULL"))
        if "ends_at" in election_window_columns and "blackout_end" in election_window_columns:
            bind.execute(text("UPDATE election_window SET blackout_end = ends_at WHERE blackout_end IS NULL"))

    inspector = sa.inspect(bind)

    if not _has_table(inspector, "audit_log"):
        op.create_table(
            "audit_log",
            sa.Column("id", sa.Uuid(), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
            sa.Column("actor", sa.String(length=255), nullable=False),
            sa.Column("action", sa.String(length=100), nullable=False),
            sa.Column("entity_type", sa.String(length=100), nullable=False),
            sa.Column("entity_id", sa.Uuid(), nullable=False),
            sa.Column("reason_code", sa.String(length=100), nullable=True),
            sa.Column("old_value", sa.JSON(), nullable=True),
            sa.Column("new_value", sa.JSON(), nullable=True),
            sa.Column("legal_basis", sa.String(length=255), nullable=True),
            sa.PrimaryKeyConstraint("id", name=op.f("pk_audit_log")),
        )
        op.create_index("ix_audit_log_created_at", "audit_log", ["created_at"], unique=False)
        op.create_index("ix_audit_log_entity_lookup", "audit_log", ["entity_type", "entity_id"], unique=False)
    else:
        audit_log_columns = _column_names_via_sql(bind, "audit_log")
        with op.batch_alter_table("audit_log") as batch_op:
            if "reason_code" not in audit_log_columns:
                batch_op.add_column(sa.Column("reason_code", sa.String(length=100), nullable=True))
            if "old_value" not in audit_log_columns:
                batch_op.add_column(sa.Column("old_value", sa.JSON(), nullable=True))
            if "new_value" not in audit_log_columns:
                batch_op.add_column(sa.Column("new_value", sa.JSON(), nullable=True))
            if "legal_basis" not in audit_log_columns:
                batch_op.add_column(sa.Column("legal_basis", sa.String(length=255), nullable=True))

        audit_log_columns = _column_names_via_sql(bind, "audit_log")
        if "diff" in audit_log_columns and "new_value" in audit_log_columns:
            bind.execute(text("UPDATE audit_log SET new_value = diff WHERE new_value IS NULL AND diff IS NOT NULL"))
            with op.batch_alter_table("audit_log") as batch_op:
                batch_op.drop_column("diff")

    if _has_table(inspector, "source_doc"):
        source_doc_columns = _column_names_via_sql(bind, "source_doc")
        with op.batch_alter_table("source_doc") as batch_op:
            if "visibility" not in source_doc_columns:
                batch_op.add_column(sa.Column("visibility", sa.String(length=20), nullable=False, server_default="VISIBLE"))
            if "public_expiry_at" not in source_doc_columns:
                batch_op.add_column(sa.Column("public_expiry_at", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if _has_table(inspector, "source_doc"):
        source_doc_columns = _column_names(inspector, "source_doc")
        with op.batch_alter_table("source_doc") as batch_op:
            if "public_expiry_at" in source_doc_columns:
                batch_op.drop_column("public_expiry_at")
            if "visibility" in source_doc_columns:
                batch_op.drop_column("visibility")

    if _has_table(inspector, "audit_log"):
        op.drop_index("ix_audit_log_entity_lookup", table_name="audit_log")
        op.drop_index("ix_audit_log_created_at", table_name="audit_log")
        op.drop_table("audit_log")

    if _has_table(inspector, "election_window"):
        op.drop_table("election_window")

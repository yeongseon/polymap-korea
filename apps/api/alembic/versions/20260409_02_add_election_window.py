from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "20260409_02"
down_revision = "20260409_01"
branch_labels = None
depends_on = None


def _has_table(inspector: sa.Inspector, table_name: str) -> bool:
    return table_name in inspector.get_table_names()


def _column_names(inspector: sa.Inspector, table_name: str) -> set[str]:
    return {column["name"] for column in inspector.get_columns(table_name)}


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if _has_table(inspector, "election_window"):
        op.drop_table("election_window")
        inspector = sa.inspect(bind)

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

    if _has_table(inspector, "audit_log") and "diff" in _column_names(inspector, "audit_log"):
        op.drop_table("audit_log")
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

    if _has_table(inspector, "source_doc"):
        source_doc_columns = _column_names(inspector, "source_doc")
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

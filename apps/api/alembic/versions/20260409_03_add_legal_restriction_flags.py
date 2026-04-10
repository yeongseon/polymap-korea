from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "20260409_03"
down_revision = "20260409_02"
branch_labels = None
depends_on = None


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())

    claim_columns = {column["name"] for column in inspector.get_columns("claim")}
    if "is_legally_restricted" not in claim_columns:
        op.add_column(
            "claim",
            sa.Column("is_legally_restricted", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        )

    source_doc_columns = {column["name"] for column in inspector.get_columns("source_doc")}
    if "is_poll_result" not in source_doc_columns:
        op.add_column(
            "source_doc",
            sa.Column("is_poll_result", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        )


def downgrade() -> None:
    inspector = sa.inspect(op.get_bind())

    source_doc_columns = {column["name"] for column in inspector.get_columns("source_doc")}
    if "is_poll_result" in source_doc_columns:
        op.drop_column("source_doc", "is_poll_result")

    claim_columns = {column["name"] for column in inspector.get_columns("claim")}
    if "is_legally_restricted" in claim_columns:
        op.drop_column("claim", "is_legally_restricted")

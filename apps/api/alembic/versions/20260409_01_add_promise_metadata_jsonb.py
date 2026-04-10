from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260409_01"
down_revision = "20260409_00"
branch_labels = None
depends_on = None


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    columns = {column["name"] for column in inspector.get_columns("promise")}
    if "metadata" not in columns:
        op.add_column("promise", sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True))


def downgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    columns = {column["name"] for column in inspector.get_columns("promise")}
    if "metadata" in columns:
        op.drop_column("promise", "metadata")

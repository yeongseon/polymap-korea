from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260409_01"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("promise", sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True))


def downgrade() -> None:
    op.drop_column("promise", "metadata")

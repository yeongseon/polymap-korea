from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260409_00"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()

    gender_enum = postgresql.ENUM("male", "female", "other", name="gender_enum")
    election_type_enum = postgresql.ENUM("local_general", "local_byelection", name="election_type_enum")
    position_type_enum = postgresql.ENUM(
        "mayor",
        "governor",
        "council_member",
        "superintendent",
        "proportional_council",
        name="position_type_enum",
    )
    candidacy_status_enum = postgresql.ENUM(
        "registered",
        "withdrawn",
        "disqualified",
        "elected",
        "defeated",
        name="candidacy_status_enum",
    )
    source_doc_kind_enum = postgresql.ENUM(
        "official_gazette",
        "news_article",
        "pdf",
        "web_page",
        "api_response",
        name="source_doc_kind_enum",
    )
    claim_type_enum = postgresql.ENUM(
        "official_fact",
        "sourced_claim",
        "opinion",
        "disputed",
        "ai_summary",
        name="claim_type_enum",
    )
    bill_status_enum = postgresql.ENUM(
        "proposed",
        "committee_review",
        "plenary",
        "passed",
        "rejected",
        "withdrawn",
        name="bill_status_enum",
    )
    issue_relation_type_enum = postgresql.ENUM("broader", "narrower", "related", name="issue_relation_type_enum")

    for enum in (
        gender_enum,
        election_type_enum,
        position_type_enum,
        candidacy_status_enum,
        source_doc_kind_enum,
        claim_type_enum,
        bill_status_enum,
        issue_relation_type_enum,
    ):
        enum.create(bind, checkfirst=True)

    op.create_table(
        "election",
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("election_type", election_type_enum, nullable=False),
        sa.Column("election_date", sa.Date(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_election")),
    )
    op.create_index("ix_election_election_date", "election", ["election_date"], unique=False)

    op.create_table(
        "district",
        sa.Column("name_ko", sa.String(length=200), nullable=False),
        sa.Column("name_en", sa.String(length=200), nullable=True),
        sa.Column("level", sa.String(length=20), nullable=False),
        sa.Column("parent_id", sa.Uuid(), nullable=True),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("geometry", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("level IN ('metropolitan', 'basic', 'constituency')", name=op.f("ck_district_level")),
        sa.ForeignKeyConstraint(["parent_id"], ["district.id"], name=op.f("fk_district_parent_id_district"), ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_district")),
        sa.UniqueConstraint("code", name=op.f("uq_district_code")),
    )

    op.create_table(
        "person",
        sa.Column("name_ko", sa.String(length=200), nullable=False),
        sa.Column("name_en", sa.String(length=200), nullable=True),
        sa.Column("birth_date", sa.Date(), nullable=True),
        sa.Column("gender", gender_enum, nullable=True),
        sa.Column("photo_url", sa.String(length=500), nullable=True),
        sa.Column("bio", sa.Text(), nullable=True),
        sa.Column("external_ids", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_person")),
    )
    op.create_index("ix_person_name_ko", "person", ["name_ko"], unique=False)

    op.create_table(
        "party",
        sa.Column("name_ko", sa.String(length=200), nullable=False),
        sa.Column("name_en", sa.String(length=200), nullable=True),
        sa.Column("abbreviation", sa.String(length=50), nullable=True),
        sa.Column("color_hex", sa.String(length=7), nullable=True),
        sa.Column("logo_url", sa.String(length=500), nullable=True),
        sa.Column("founded_date", sa.Date(), nullable=True),
        sa.Column("dissolved_date", sa.Date(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "color_hex IS NULL OR (length(color_hex) = 7 AND substr(color_hex, 1, 1) = '#')",
            name=op.f("ck_party_color_hex_format"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_party")),
        sa.UniqueConstraint("name_ko", name=op.f("uq_party_name_ko")),
    )

    op.create_table(
        "issue",
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("slug", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("parent_id", sa.Uuid(), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["parent_id"], ["issue.id"], name=op.f("fk_issue_parent_id_issue"), ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_issue")),
        sa.UniqueConstraint("name", name=op.f("uq_issue_name")),
        sa.UniqueConstraint("slug", name=op.f("uq_issue_slug")),
    )

    op.create_table(
        "source_doc",
        sa.Column("kind", source_doc_kind_enum, nullable=False),
        sa.Column("title", sa.String(length=300), nullable=False),
        sa.Column("url", sa.String(length=1000), nullable=True),
        sa.Column("published_at", sa.DateTime(), nullable=True),
        sa.Column("visibility", sa.String(length=20), nullable=False, server_default=sa.text("'VISIBLE'")),
        sa.Column("is_poll_result", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("public_expiry_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("content_hash", sa.String(length=128), nullable=True),
        sa.Column("raw_s3_key", sa.String(length=500), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_source_doc")),
    )

    op.create_table(
        "race",
        sa.Column("election_id", sa.Uuid(), nullable=False),
        sa.Column("district_id", sa.Uuid(), nullable=False),
        sa.Column("position_type", position_type_enum, nullable=False),
        sa.Column("seat_count", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("seat_count >= 1", name=op.f("ck_race_seat_count_positive")),
        sa.ForeignKeyConstraint(["district_id"], ["district.id"], name=op.f("fk_race_district_id_district"), ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["election_id"], ["election.id"], name=op.f("fk_race_election_id_election"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_race")),
        sa.UniqueConstraint("election_id", "district_id", "position_type", name=op.f("uq_race_race_scope")),
    )

    op.create_table(
        "candidacy",
        sa.Column("person_id", sa.Uuid(), nullable=False),
        sa.Column("race_id", sa.Uuid(), nullable=False),
        sa.Column("party_id", sa.Uuid(), nullable=True),
        sa.Column("status", candidacy_status_enum, nullable=False, server_default="registered"),
        sa.Column("registered_at", sa.Date(), nullable=True),
        sa.Column("candidate_number", sa.Integer(), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint(
            "candidate_number IS NULL OR candidate_number >= 1",
            name=op.f("ck_candidacy_candidate_number_positive"),
        ),
        sa.ForeignKeyConstraint(["party_id"], ["party.id"], name=op.f("fk_candidacy_party_id_party"), ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["person_id"], ["person.id"], name=op.f("fk_candidacy_person_id_person"), ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["race_id"], ["race.id"], name=op.f("fk_candidacy_race_id_race"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_candidacy")),
        sa.UniqueConstraint("person_id", "race_id", name=op.f("uq_candidacy_person_race")),
    )

    op.create_table(
        "issue_relation",
        sa.Column("source_issue_id", sa.Uuid(), nullable=False),
        sa.Column("target_issue_id", sa.Uuid(), nullable=False),
        sa.Column("relation_type", issue_relation_type_enum, nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("source_issue_id <> target_issue_id", name=op.f("ck_issue_relation_distinct_issue_nodes")),
        sa.ForeignKeyConstraint(["source_issue_id"], ["issue.id"], name=op.f("fk_issue_relation_source_issue_id_issue"), ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["target_issue_id"], ["issue.id"], name=op.f("fk_issue_relation_target_issue_id_issue"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_issue_relation")),
        sa.UniqueConstraint("source_issue_id", "target_issue_id", "relation_type", name=op.f("uq_issue_relation_source_target_relation")),
    )

    op.create_table(
        "promise",
        sa.Column("candidacy_id", sa.Uuid(), nullable=False),
        sa.Column("title", sa.String(length=300), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("category", sa.String(length=100), nullable=True),
        sa.Column("issue_id", sa.Uuid(), nullable=True),
        sa.Column("source_doc_id", sa.Uuid(), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["candidacy_id"], ["candidacy.id"], name=op.f("fk_promise_candidacy_id_candidacy"), ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["issue_id"], ["issue.id"], name=op.f("fk_promise_issue_id_issue"), ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["source_doc_id"], ["source_doc.id"], name=op.f("fk_promise_source_doc_id_source_doc"), ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_promise")),
    )
    op.create_index(
        "ix_promise_body_tsv",
        "promise",
        [sa.text("to_tsvector('simple', body)")],
        unique=False,
        postgresql_using="gin",
    )

    op.create_table(
        "claim",
        sa.Column("source_doc_id", sa.Uuid(), nullable=False),
        sa.Column("candidacy_id", sa.Uuid(), nullable=False),
        sa.Column("claim_type", claim_type_enum, nullable=False),
        sa.Column("is_legally_restricted", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("excerpt", sa.Text(), nullable=True),
        sa.Column("extracted_at", sa.DateTime(), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["candidacy_id"], ["candidacy.id"], name=op.f("fk_claim_candidacy_id_candidacy"), ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["source_doc_id"], ["source_doc.id"], name=op.f("fk_claim_source_doc_id_source_doc"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_claim")),
    )
    op.create_index(
        "ix_claim_content_tsv",
        "claim",
        [sa.text("to_tsvector('simple', content)")],
        unique=False,
        postgresql_using="gin",
    )

    op.create_table(
        "committee_assignment",
        sa.Column("person_id", sa.Uuid(), nullable=False),
        sa.Column("committee_name", sa.String(length=200), nullable=False),
        sa.Column("role", sa.String(length=100), nullable=True),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("source_doc_id", sa.Uuid(), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["person_id"], ["person.id"], name=op.f("fk_committee_assignment_person_id_person"), ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["source_doc_id"], ["source_doc.id"], name=op.f("fk_committee_assignment_source_doc_id_source_doc"), ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_committee_assignment")),
    )

    op.create_table(
        "bill_sponsorship",
        sa.Column("person_id", sa.Uuid(), nullable=False),
        sa.Column("bill_name", sa.String(length=300), nullable=False),
        sa.Column("bill_id_external", sa.String(length=100), nullable=True),
        sa.Column("role", sa.String(length=20), nullable=False, server_default="lead_sponsor"),
        sa.Column("status", bill_status_enum, nullable=False),
        sa.Column("proposed_date", sa.Date(), nullable=True),
        sa.Column("source_doc_id", sa.Uuid(), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("role IN ('lead_sponsor', 'co_sponsor')", name=op.f("ck_bill_sponsorship_role")),
        sa.ForeignKeyConstraint(["person_id"], ["person.id"], name=op.f("fk_bill_sponsorship_person_id_person"), ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["source_doc_id"], ["source_doc.id"], name=op.f("fk_bill_sponsorship_source_doc_id_source_doc"), ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_bill_sponsorship")),
    )

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

    op.create_table(
        "audit_log",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("actor", sa.String(length=255), nullable=False),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("entity_type", sa.String(length=100), nullable=False),
        sa.Column("entity_id", sa.Uuid(), nullable=False),
        sa.Column("reason_code", sa.String(length=100), nullable=True),
        sa.Column("old_value", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("new_value", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("legal_basis", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_audit_log")),
    )
    op.create_index("ix_audit_log_created_at", "audit_log", ["created_at"], unique=False)
    op.create_index("ix_audit_log_entity_lookup", "audit_log", ["entity_type", "entity_id"], unique=False)


def downgrade() -> None:
    bind = op.get_bind()

    op.drop_index("ix_audit_log_entity_lookup", table_name="audit_log")
    op.drop_index("ix_audit_log_created_at", table_name="audit_log")
    op.drop_table("audit_log")
    op.drop_table("election_window")
    op.drop_table("bill_sponsorship")
    op.drop_table("committee_assignment")
    op.drop_index("ix_claim_content_tsv", table_name="claim")
    op.drop_table("claim")
    op.drop_index("ix_promise_body_tsv", table_name="promise")
    op.drop_table("promise")
    op.drop_table("issue_relation")
    op.drop_table("candidacy")
    op.drop_table("race")
    op.drop_table("source_doc")
    op.drop_table("issue")
    op.drop_table("party")
    op.drop_index("ix_person_name_ko", table_name="person")
    op.drop_table("person")
    op.drop_table("district")
    op.drop_index("ix_election_election_date", table_name="election")
    op.drop_table("election")

    for enum in (
        postgresql.ENUM(name="issue_relation_type_enum"),
        postgresql.ENUM(name="bill_status_enum"),
        postgresql.ENUM(name="claim_type_enum"),
        postgresql.ENUM(name="source_doc_kind_enum"),
        postgresql.ENUM(name="candidacy_status_enum"),
        postgresql.ENUM(name="position_type_enum"),
        postgresql.ENUM(name="election_type_enum"),
        postgresql.ENUM(name="gender_enum"),
    ):
        enum.drop(bind, checkfirst=True)

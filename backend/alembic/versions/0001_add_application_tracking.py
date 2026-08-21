"""Add application tracking tables.

Revision ID: 0001_application_tracking
Revises:
Create Date: 2026-08-21
"""

from alembic import op
import sqlalchemy as sa


revision = "0001_application_tracking"
down_revision = None
branch_labels = None
depends_on = None


def table_exists(table_name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return table_name in inspector.get_table_names()


def upgrade() -> None:
    # ------------------------------------------------------------
    # Application events
    # ------------------------------------------------------------
    if not table_exists("application_events"):
        op.create_table(
            "application_events",
            sa.Column(
                "id",
                sa.Integer(),
                primary_key=True,
            ),
            sa.Column(
                "application_id",
                sa.Integer(),
                sa.ForeignKey(
                    "applications.id",
                    ondelete="CASCADE",
                ),
                nullable=False,
            ),
            sa.Column(
                "event_type",
                sa.String(length=40),
                nullable=False,
            ),
            sa.Column(
                "title",
                sa.String(length=160),
                nullable=False,
            ),
            sa.Column(
                "description",
                sa.Text(),
                nullable=True,
            ),
            sa.Column(
                "created_at",
                sa.DateTime(),
                nullable=False,
            ),
        )

        op.create_index(
            "ix_application_events_application_id",
            "application_events",
            ["application_id"],
        )

        op.create_index(
            "ix_application_events_event_type",
            "application_events",
            ["event_type"],
        )

        op.create_index(
            "ix_application_events_created_at",
            "application_events",
            ["created_at"],
        )

    # ------------------------------------------------------------
    # Interviews
    # ------------------------------------------------------------
    if not table_exists("interviews"):
        op.create_table(
            "interviews",
            sa.Column(
                "id",
                sa.Integer(),
                primary_key=True,
            ),
            sa.Column(
                "application_id",
                sa.Integer(),
                sa.ForeignKey(
                    "applications.id",
                    ondelete="CASCADE",
                ),
                nullable=False,
            ),
            sa.Column(
                "interview_type",
                sa.String(length=60),
                nullable=False,
            ),
            sa.Column(
                "scheduled_at",
                sa.DateTime(),
                nullable=False,
            ),
            sa.Column(
                "duration_minutes",
                sa.Integer(),
                nullable=True,
            ),
            sa.Column(
                "interviewer",
                sa.String(length=160),
                nullable=True,
            ),
            sa.Column(
                "meeting_url",
                sa.String(length=500),
                nullable=True,
            ),
            sa.Column(
                "notes",
                sa.Text(),
                nullable=True,
            ),
            sa.Column(
                "status",
                sa.String(length=30),
                nullable=False,
            ),
        )

        op.create_index(
            "ix_interviews_application_id",
            "interviews",
            ["application_id"],
        )

        op.create_index(
            "ix_interviews_scheduled_at",
            "interviews",
            ["scheduled_at"],
        )

        op.create_index(
            "ix_interviews_status",
            "interviews",
            ["status"],
        )

    # ------------------------------------------------------------
    # Follow-ups
    # ------------------------------------------------------------
    if not table_exists("follow_ups"):
        op.create_table(
            "follow_ups",
            sa.Column(
                "id",
                sa.Integer(),
                primary_key=True,
            ),
            sa.Column(
                "application_id",
                sa.Integer(),
                sa.ForeignKey(
                    "applications.id",
                    ondelete="CASCADE",
                ),
                nullable=False,
            ),
            sa.Column(
                "scheduled_for",
                sa.DateTime(),
                nullable=False,
            ),
            sa.Column(
                "completed_at",
                sa.DateTime(),
                nullable=True,
            ),
            sa.Column(
                "note",
                sa.String(length=500),
                nullable=False,
            ),
            sa.Column(
                "status",
                sa.String(length=30),
                nullable=False,
            ),
        )

        op.create_index(
            "ix_follow_ups_application_id",
            "follow_ups",
            ["application_id"],
        )

        op.create_index(
            "ix_follow_ups_scheduled_for",
            "follow_ups",
            ["scheduled_for"],
        )

        op.create_index(
            "ix_follow_ups_status",
            "follow_ups",
            ["status"],
        )


def downgrade() -> None:
    # Remove only the tables introduced by this migration.
    # Existing CareerFlow tables are intentionally untouched.
    if table_exists("follow_ups"):
        op.drop_table("follow_ups")

    if table_exists("interviews"):
        op.drop_table("interviews")

    if table_exists("application_events"):
        op.drop_table("application_events")

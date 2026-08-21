"""Add application tracking and missing application columns.

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


def get_inspector():
    bind = op.get_bind()
    return sa.inspect(bind)


def table_exists(table_name: str) -> bool:
    return table_name in get_inspector().get_table_names()


def column_exists(table_name: str, column_name: str) -> bool:
    columns = get_inspector().get_columns(table_name)
    return any(column["name"] == column_name for column in columns)


def upgrade() -> None:

    # ============================================================
    # EXISTING APPLICATION COLUMNS
    # ============================================================
    #
    # These columns were previously created by main.py.
    # We now manage them through Alembic instead.
    #
    if table_exists("applications"):

        if not column_exists(
            "applications",
            "employment_type",
        ):
            op.add_column(
                "applications",
                sa.Column(
                    "employment_type",
                    sa.String(length=30),
                    nullable=True,
                    server_default="Full-time",
                ),
            )

        if not column_exists(
            "applications",
            "work_mode",
        ):
            op.add_column(
                "applications",
                sa.Column(
                    "work_mode",
                    sa.String(length=20),
                    nullable=True,
                    server_default="Unknown",
                ),
            )

        if not column_exists(
            "applications",
            "salary",
        ):
            op.add_column(
                "applications",
                sa.Column(
                    "salary",
                    sa.String(length=80),
                    nullable=True,
                ),
            )

        if not column_exists(
            "applications",
            "priority",
        ):
            op.add_column(
                "applications",
                sa.Column(
                    "priority",
                    sa.String(length=20),
                    nullable=True,
                    server_default="Normal",
                ),
            )

        if not column_exists(
            "applications",
            "next_step",
        ):
            op.add_column(
                "applications",
                sa.Column(
                    "next_step",
                    sa.String(length=180),
                    nullable=True,
                ),
            )

        if not column_exists(
            "applications",
            "job_url",
        ):
            op.add_column(
                "applications",
                sa.Column(
                    "job_url",
                    sa.String(length=500),
                    nullable=True,
                ),
            )

        if not column_exists(
            "applications",
            "source",
        ):
            op.add_column(
                "applications",
                sa.Column(
                    "source",
                    sa.String(length=80),
                    nullable=True,
                    server_default="Manual",
                ),
            )

    # ============================================================
    # APPLICATION EVENTS
    # ============================================================

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

    # ============================================================
    # INTERVIEWS
    # ============================================================

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
                server_default="Scheduled",
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

    # ============================================================
    # FOLLOW-UPS
    # ============================================================

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
                server_default="Pending",
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

    # Remove only objects introduced by this migration.
    # Existing users, applications and feedback remain untouched.

    if table_exists("follow_ups"):
        op.drop_table("follow_ups")

    if table_exists("interviews"):
        op.drop_table("interviews")

    if table_exists("application_events"):
        op.drop_table("application_events")

    # Remove application columns only if this migration added them.
    #
    # We intentionally do not remove these columns here because some
    # older CareerFlow deployments may already have had them before
    # Alembic was introduced.

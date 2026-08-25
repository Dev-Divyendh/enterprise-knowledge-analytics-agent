"""create analytics reader role

Revision ID: 55a2a6b3f72c
Revises: 1594d5b9258b
Create Date: 2026-08-25 01:58:14.514981

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "55a2a6b3f72c"
down_revision: str | Sequence[str] | None = "1594d5b9258b"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

ANALYTICS_READER_ROLE = "enterprise_agent_analytics_reader"


def upgrade() -> None:
    """Create a non-login role with approved read-only analytics access."""

    op.execute(f"CREATE ROLE {ANALYTICS_READER_ROLE} NOLOGIN")
    op.execute(f"GRANT USAGE ON SCHEMA analytics TO {ANALYTICS_READER_ROLE}")
    op.execute(
        "GRANT SELECT ON TABLE "
        "analytics.departments, "
        "analytics.expense_reports, "
        "analytics.expense_items "
        f"TO {ANALYTICS_READER_ROLE}"
    )
    op.execute(
        "GRANT SELECT ("
        "id, employee_number, department_id, display_name, "
        "job_title, hire_date, employment_status"
        ") ON TABLE analytics.employees "
        f"TO {ANALYTICS_READER_ROLE}"
    )


def downgrade() -> None:
    """Remove the analytics reader role and its permissions."""

    op.execute(
        "REVOKE SELECT ("
        "id, employee_number, department_id, display_name, "
        "job_title, hire_date, employment_status"
        ") ON TABLE analytics.employees "
        f"FROM {ANALYTICS_READER_ROLE}"
    )
    op.execute(
        "REVOKE SELECT ON TABLE "
        "analytics.departments, "
        "analytics.expense_reports, "
        "analytics.expense_items "
        f"FROM {ANALYTICS_READER_ROLE}"
    )
    op.execute(f"REVOKE USAGE ON SCHEMA analytics FROM {ANALYTICS_READER_ROLE}")
    op.execute(f"DROP ROLE {ANALYTICS_READER_ROLE}")

"""enable vector extension

Revision ID: 7452c28b9a1e
Revises:
Create Date: 2026-08-20 02:08:39.433567

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "7452c28b9a1e"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Enable pgvector in the application database."""

    op.execute("CREATE EXTENSION IF NOT EXISTS vector")


def downgrade() -> None:
    """Remove pgvector after dependent objects have been removed."""

    op.execute("DROP EXTENSION IF EXISTS vector")

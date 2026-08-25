from collections.abc import Iterator
from decimal import Decimal

import pytest
from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import Engine, text
from sqlalchemy.exc import DBAPIError, IntegrityError

from enterprise_knowledge_analytics_agent.config import get_settings
from enterprise_knowledge_analytics_agent.persistence.database import (
    create_database_engine,
)
from enterprise_knowledge_analytics_agent.persistence.seed_analytics import (
    seed_analytics_data,
)

pytestmark = pytest.mark.integration

EXPECTED_TABLES = {
    "analytics.departments",
    "analytics.employees",
    "analytics.expense_items",
    "analytics.expense_reports",
    "public.alembic_version",
    "public.chunks",
    "public.document_versions",
    "public.documents",
    "public.embeddings",
    "public.evaluation_runs",
    "public.processing_runs",
}


@pytest.fixture(scope="module")
def database_engine() -> Iterator[Engine]:
    """Provide a connection pool for tests requiring local PostgreSQL."""

    settings = get_settings()

    if settings.database_url is None:
        pytest.skip("EKA_DATABASE_URL is not configured")

    engine = create_database_engine(settings)
    yield engine
    engine.dispose()


def test_database_is_at_latest_migration(database_engine: Engine) -> None:
    alembic_config = Config("alembic.ini")
    migration_scripts = ScriptDirectory.from_config(alembic_config)
    expected_head = migration_scripts.get_current_head()

    with database_engine.connect() as connection:
        migration_context = MigrationContext.configure(connection)
        actual_revision = migration_context.get_current_revision()

    assert actual_revision == expected_head


def test_pgvector_extension_is_available(database_engine: Engine) -> None:
    with database_engine.connect() as connection:
        version = connection.execute(
            text("SELECT extversion FROM pg_extension WHERE extname = 'vector'")
        ).scalar_one()

    assert version == "0.8.6"


def test_expected_tables_exist(database_engine: Engine) -> None:
    with database_engine.connect() as connection:
        tables = connection.execute(
            text(
                "SELECT schemaname || '.' || tablename "
                "FROM pg_tables "
                "WHERE schemaname IN ('public', 'analytics')"
            )
        ).scalars()

        actual_tables = set(tables)

    assert actual_tables == EXPECTED_TABLES


def test_seed_operation_is_idempotent(database_engine: Engine) -> None:
    first_result = seed_analytics_data()
    second_result = seed_analytics_data()

    expected_counts = {
        "departments": 6,
        "employees": 12,
        "expense_reports": 24,
        "expense_items": 72,
    }

    assert first_result == expected_counts
    assert second_result == expected_counts

    with database_engine.connect() as connection:
        counts = connection.execute(
            text(
                "SELECT "
                "(SELECT COUNT(*) FROM analytics.departments), "
                "(SELECT COUNT(*) FROM analytics.employees), "
                "(SELECT COUNT(*) FROM analytics.expense_reports), "
                "(SELECT COUNT(*) FROM analytics.expense_items)"
            )
        ).one()

    assert tuple(counts) == (6, 12, 24, 72)


def test_reader_can_execute_approved_query(database_engine: Engine) -> None:
    with database_engine.connect() as connection:
        connection.execute(text("SET LOCAL ROLE enterprise_agent_analytics_reader"))
        total = connection.execute(
            text("SELECT SUM(amount) FROM analytics.expense_items")
        ).scalar_one()

    assert total == Decimal("28500.00")


def test_reader_cannot_read_salary(database_engine: Engine) -> None:
    with pytest.raises(DBAPIError):
        with database_engine.connect() as connection:
            connection.execute(text("SET LOCAL ROLE enterprise_agent_analytics_reader"))
            connection.execute(text("SELECT annual_salary FROM analytics.employees")).all()


def test_reader_cannot_write(database_engine: Engine) -> None:
    with pytest.raises(DBAPIError):
        with database_engine.connect() as connection:
            connection.execute(text("SET LOCAL ROLE enterprise_agent_analytics_reader"))
            connection.execute(text("UPDATE analytics.expense_items SET amount = amount + 1"))


def test_database_rejects_nonpositive_expense(
    database_engine: Engine,
) -> None:
    with pytest.raises(IntegrityError):
        with database_engine.begin() as connection:
            connection.execute(
                text(
                    "UPDATE analytics.expense_items "
                    "SET amount = 0 "
                    "WHERE id = ("
                    "SELECT id FROM analytics.expense_items LIMIT 1"
                    ")"
                )
            )

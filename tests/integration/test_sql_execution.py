from decimal import Decimal

import pytest

from enterprise_knowledge_analytics_agent.analytics.sql import (
    execute_validated_sql,
    validate_sql,
)
from enterprise_knowledge_analytics_agent.persistence.database import (
    create_database_engine,
)
from enterprise_knowledge_analytics_agent.persistence.seed_analytics import (
    seed_analytics_data,
)

pytestmark = pytest.mark.integration

ENGINEERING_SPEND_SQL = """
SELECT
    d.name AS department,
    COUNT(DISTINCT r.id) AS report_count,
    SUM(i.amount) AS total_usd
FROM analytics.departments AS d
JOIN analytics.employees AS e
  ON e.department_id = d.id
JOIN analytics.expense_reports AS r
  ON r.employee_id = e.id
JOIN analytics.expense_items AS i
  ON i.report_id = r.id
WHERE d.name = 'Engineering'
  AND r.status = 'paid'
  AND r.submitted_date >= DATE '2025-01-01'
  AND r.submitted_date < DATE '2026-01-01'
GROUP BY d.name
"""


def test_validated_engineering_spend_query_executes_read_only() -> None:
    seed_analytics_data()
    engine = create_database_engine()

    try:
        validated = validate_sql(ENGINEERING_SPEND_SQL)
        result = execute_validated_sql(
            validated,
            engine=engine,
        )
    finally:
        engine.dispose()

    assert result.columns == [
        "department",
        "report_count",
        "total_usd",
    ]
    assert result.row_count == 1
    assert result.rows[0]["department"] == "Engineering"
    assert result.rows[0]["report_count"] == 4
    assert result.rows[0]["total_usd"] == Decimal("3250.00")
    assert result.elapsed_ms > 0

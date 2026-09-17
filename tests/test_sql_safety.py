import pytest

from enterprise_knowledge_analytics_agent.analytics.sql import (
    SQLValidationError,
    validate_sql,
)

APPROVED_SQL = """
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


def test_approved_select_receives_mandatory_limit() -> None:
    validated = validate_sql(APPROVED_SQL)

    assert validated.row_limit == 100
    assert validated.sql.endswith("LIMIT 100")
    assert validated.tables == (
        "departments",
        "employees",
        "expense_items",
        "expense_reports",
    )
    assert "amount" in validated.columns


def test_destructive_statement_is_rejected() -> None:
    with pytest.raises(SQLValidationError, match="only SELECT"):
        validate_sql("DELETE FROM analytics.expense_items")


def test_multiple_statements_are_rejected() -> None:
    with pytest.raises(SQLValidationError, match="exactly one"):
        validate_sql("SELECT id FROM analytics.departments; DELETE FROM analytics.expense_items")


def test_non_allowlisted_schema_is_rejected() -> None:
    with pytest.raises(SQLValidationError, match="analytics schema"):
        validate_sql("SELECT id FROM public.documents")


def test_restricted_salary_column_is_rejected() -> None:
    with pytest.raises(SQLValidationError, match="restricted"):
        validate_sql("SELECT e.annual_salary FROM analytics.employees AS e")


def test_wildcard_is_rejected() -> None:
    with pytest.raises(SQLValidationError, match="wildcard"):
        validate_sql("SELECT * FROM analytics.departments")


def test_excessive_limit_is_rejected() -> None:
    with pytest.raises(SQLValidationError, match="LIMIT must be between"):
        validate_sql("SELECT d.name FROM analytics.departments AS d LIMIT 1000")


def test_unapproved_function_is_rejected() -> None:
    with pytest.raises(SQLValidationError, match="functions"):
        validate_sql("SELECT pg_sleep(10) FROM analytics.departments AS d")

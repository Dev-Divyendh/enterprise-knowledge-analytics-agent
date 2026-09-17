import json
from collections.abc import Mapping
from typing import Any

import pytest

from enterprise_knowledge_analytics_agent.analytics.service import (
    APPROVED_ENGINEERING_QUESTION,
    answer_analytics_question,
    answer_approved_engineering_question,
)
from enterprise_knowledge_analytics_agent.analytics.sql import SQLValidationError
from enterprise_knowledge_analytics_agent.persistence.database import (
    create_database_engine,
)
from enterprise_knowledge_analytics_agent.persistence.seed_analytics import (
    seed_analytics_data,
)
from enterprise_knowledge_analytics_agent.rag.providers import GenerationResult

pytestmark = pytest.mark.integration

GENERATED_SQL = """
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

INCORRECT_REAL_MODEL_SQL = """
SELECT
    SUM(i.amount) AS total_spent
FROM analytics.expense_reports AS r
JOIN analytics.employees AS e
  ON r.employee_id = e.id
JOIN analytics.departments AS d
  ON e.department_id = d.id
JOIN analytics.expense_items AS i
  ON r.id = i.report_id
WHERE d.name = 'Engineering'
  AND r.status = 'paid'
  AND r.trip_start_date >= DATE '2025-01-01'
  AND r.trip_end_date < DATE '2026-01-01'
"""


class DeterministicSQLProvider:
    """Return predictable structured SQL without calling Ollama."""

    def __init__(self, sql: str = GENERATED_SQL) -> None:
        self.sql = sql
        self.call_count = 0

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        response_format: Mapping[str, Any],
    ) -> GenerationResult:
        self.call_count += 1

        assert "exactly one SELECT" in system_prompt
        assert "annual_salary" not in user_prompt
        assert APPROVED_ENGINEERING_QUESTION in user_prompt
        assert response_format["type"] == "object"

        return GenerationResult(
            content=json.dumps({"sql": self.sql}),
            model="deterministic-sql-provider",
            prompt_tokens=150,
            completion_tokens=100,
            latency_ms=1.0,
        )


def test_approved_question_generates_validates_and_executes_sql() -> None:
    seed_analytics_data()
    engine = create_database_engine()
    provider = DeterministicSQLProvider()

    try:
        answer = answer_analytics_question(
            APPROVED_ENGINEERING_QUESTION,
            llm_provider=provider,
            engine=engine,
        )
    finally:
        engine.dispose()

    assert answer.status == "answered"
    assert answer.answer == ("Engineering had 4 paid expense reports totaling $3,250.00 in 2025.")
    assert answer.sql is not None
    assert answer.sql.endswith("LIMIT 100")
    assert answer.rows == [
        {
            "department": "Engineering",
            "report_count": 4,
            "total_usd": answer.rows[0]["total_usd"],
        }
    ]
    assert str(answer.rows[0]["total_usd"]) == "3250.00"
    assert answer.llm_model == "deterministic-sql-provider"
    assert provider.call_count == 1


def test_semantically_incorrect_real_model_query_is_rejected() -> None:
    engine = create_database_engine()
    provider = DeterministicSQLProvider(INCORRECT_REAL_MODEL_SQL)

    try:
        with pytest.raises(
            SQLValidationError,
            match="required result columns",
        ):
            answer_approved_engineering_question(
                APPROVED_ENGINEERING_QUESTION,
                llm_provider=provider,
                engine=engine,
            )
    finally:
        engine.dispose()

    assert provider.call_count == 1

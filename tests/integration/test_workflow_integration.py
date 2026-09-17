import json
from collections.abc import Iterator, Mapping
from pathlib import Path
from typing import Any

import pytest
from sqlalchemy import Engine

from enterprise_knowledge_analytics_agent.analytics.service import (
    APPROVED_ENGINEERING_QUESTION,
)
from enterprise_knowledge_analytics_agent.ingestion.service import ingest_markdown
from enterprise_knowledge_analytics_agent.persistence.database import (
    create_database_engine,
)
from enterprise_knowledge_analytics_agent.persistence.seed_analytics import (
    seed_analytics_data,
)
from enterprise_knowledge_analytics_agent.rag.providers import GenerationResult
from enterprise_knowledge_analytics_agent.retrieval.dense import (
    embed_document_chunks,
)
from enterprise_knowledge_analytics_agent.retrieval.embeddings import (
    SentenceTransformerEmbeddingProvider,
)
from enterprise_knowledge_analytics_agent.workflow.graph import run_workflow

pytestmark = pytest.mark.integration

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
DOC_001_PATH = REPOSITORY_ROOT / "data" / "documents" / "DOC-001-parental-leave-policy.md"

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


class DeterministicWorkflowLLMProvider:
    """Return deterministic structured output for both executing routes."""

    def __init__(self) -> None:
        self.rag_call_count = 0
        self.sql_call_count = 0

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        response_format: Mapping[str, Any],
    ) -> GenerationResult:
        properties = response_format.get("properties")

        if not isinstance(properties, dict):
            raise AssertionError("response schema must contain properties")

        if "citation_ranks" in properties:
            self.rag_call_count += 1

            assert "untrusted data" in system_prompt
            assert "12 weeks" in user_prompt

            content = json.dumps(
                {
                    "answer": (
                        "Eligible employees may receive up to 12 weeks of paid parental leave."
                    ),
                    "citation_ranks": [1],
                }
            )
        elif "sql" in properties:
            self.sql_call_count += 1

            assert "exactly one SELECT" in system_prompt
            assert APPROVED_ENGINEERING_QUESTION in user_prompt

            content = json.dumps(
                {
                    "sql": APPROVED_SQL,
                }
            )
        else:
            raise AssertionError("unexpected structured-output schema")

        return GenerationResult(
            content=content,
            model="deterministic-workflow-provider",
            prompt_tokens=100,
            completion_tokens=20,
            latency_ms=1.0,
        )


@pytest.fixture(scope="module")
def workflow_dependencies() -> Iterator[
    tuple[
        Engine,
        SentenceTransformerEmbeddingProvider,
        DeterministicWorkflowLLMProvider,
    ]
]:
    seed_analytics_data()

    engine = create_database_engine()
    embedding_provider = SentenceTransformerEmbeddingProvider()
    llm_provider = DeterministicWorkflowLLMProvider()

    ingest_markdown(DOC_001_PATH, engine)
    embed_document_chunks(
        external_id="DOC-001",
        provider=embedding_provider,
        engine=engine,
    )

    yield engine, embedding_provider, llm_provider
    engine.dispose()


def test_graph_executes_policy_rag_branch(
    workflow_dependencies: tuple[
        Engine,
        SentenceTransformerEmbeddingProvider,
        DeterministicWorkflowLLMProvider,
    ],
) -> None:
    engine, embedding_provider, llm_provider = workflow_dependencies

    answer = run_workflow(
        "How many weeks of paid parental leave are available?",
        llm_provider=llm_provider,
        embedding_provider=embedding_provider,
        engine=engine,
    )

    assert answer.route == "policy_rag"
    assert answer.abstained is False
    assert "12 weeks" in answer.answer
    assert answer.citations[0].document_id == "DOC-001"
    assert answer.citations[0].section == "Paid Parental Leave"
    assert answer.sql is None
    assert llm_provider.rag_call_count == 1
    assert llm_provider.sql_call_count == 0


def test_graph_executes_text_to_sql_branch(
    workflow_dependencies: tuple[
        Engine,
        SentenceTransformerEmbeddingProvider,
        DeterministicWorkflowLLMProvider,
    ],
) -> None:
    engine, embedding_provider, llm_provider = workflow_dependencies

    answer = run_workflow(
        APPROVED_ENGINEERING_QUESTION,
        llm_provider=llm_provider,
        embedding_provider=embedding_provider,
        engine=engine,
    )

    assert answer.route == "text_to_sql"
    assert answer.answer == ("Engineering had 4 paid expense reports totaling $3,250.00 in 2025.")
    assert answer.sql is not None
    assert answer.sql.endswith("LIMIT 100")
    assert answer.rows[0]["department"] == "Engineering"
    assert str(answer.rows[0]["total_usd"]) == "3250.00"
    assert answer.citations == []
    assert llm_provider.rag_call_count == 1
    assert llm_provider.sql_call_count == 1

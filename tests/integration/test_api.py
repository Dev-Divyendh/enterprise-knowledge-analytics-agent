import json
from collections.abc import Iterator, Mapping
from pathlib import Path
from typing import Any, Protocol, cast

import httpx
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine

from enterprise_knowledge_analytics_agent.analytics.service import (
    APPROVED_ENGINEERING_QUESTION,
    DESTRUCTIVE_REQUEST,
)
from enterprise_knowledge_analytics_agent.api.app import app
from enterprise_knowledge_analytics_agent.api.dependencies import (
    get_database_engine,
    get_embedding_provider,
    get_llm_provider,
)
from enterprise_knowledge_analytics_agent.ingestion.service import ingest_markdown
from enterprise_knowledge_analytics_agent.persistence.database import (
    create_database_engine,
)
from enterprise_knowledge_analytics_agent.persistence.seed_analytics import (
    seed_analytics_data,
)
from enterprise_knowledge_analytics_agent.rag.providers import (
    GenerationResult,
    LLMProvider,
)
from enterprise_knowledge_analytics_agent.retrieval.dense import (
    embed_document_chunks,
)
from enterprise_knowledge_analytics_agent.retrieval.embeddings import (
    EmbeddingProvider,
    SentenceTransformerEmbeddingProvider,
)
from enterprise_knowledge_analytics_agent.workflow.domain import WorkflowAnswer

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


class _ApiClient(Protocol):
    """Typed subset of TestClient used by these tests."""

    def post(
        self,
        url: str,
        *,
        json: object,
    ) -> httpx.Response:
        """Send one JSON POST request."""

        ...


class DeterministicLLMProvider:
    """Predictable provider supporting RAG and SQL output schemas."""

    def __init__(self) -> None:
        self.call_count = 0

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        response_format: Mapping[str, Any],
    ) -> GenerationResult:
        self.call_count += 1
        properties = response_format.get("properties")

        if not isinstance(properties, dict):
            raise AssertionError("response schema must contain properties")

        if "citation_ranks" in properties:
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
            assert "exactly one SELECT" in system_prompt
            assert APPROVED_ENGINEERING_QUESTION in user_prompt

            content = json.dumps({"sql": APPROVED_SQL})
        else:
            raise AssertionError("unexpected structured-output schema")

        return GenerationResult(
            content=content,
            model="deterministic-api-test-double",
            prompt_tokens=100,
            completion_tokens=20,
            latency_ms=1.0,
        )


@pytest.fixture(scope="module")
def api_dependencies() -> Iterator[tuple[_ApiClient, DeterministicLLMProvider]]:
    """Prepare real retrieval and SQL paths with a deterministic LLM."""

    seed_analytics_data()

    engine = create_database_engine()
    embedding_provider = SentenceTransformerEmbeddingProvider()
    llm_provider = DeterministicLLMProvider()

    ingest_markdown(DOC_001_PATH, engine)
    embed_document_chunks(
        external_id="DOC-001",
        provider=embedding_provider,
        engine=engine,
    )

    def override_database_engine() -> Engine:
        return engine

    def override_embedding_provider() -> EmbeddingProvider:
        return embedding_provider

    def override_llm_provider() -> LLMProvider:
        return llm_provider

    app.dependency_overrides[get_database_engine] = override_database_engine
    app.dependency_overrides[get_embedding_provider] = override_embedding_provider
    app.dependency_overrides[get_llm_provider] = override_llm_provider

    with TestClient(app) as client:
        yield cast(_ApiClient, client), llm_provider

    app.dependency_overrides.clear()
    engine.dispose()


def test_supported_policy_question_returns_citation(
    api_dependencies: tuple[_ApiClient, DeterministicLLMProvider],
) -> None:
    client, llm_provider = api_dependencies
    calls_before = llm_provider.call_count

    response = client.post(
        "/api/v1/questions",
        json={"question": ("How many weeks of paid parental leave are available?")},
    )

    assert response.status_code == 200

    answer = WorkflowAnswer.model_validate_json(response.text)

    assert answer.route == "policy_rag"
    assert answer.abstained is False
    assert "12 weeks" in answer.answer
    assert len(answer.citations) == 1
    assert answer.citations[0].document_id == "DOC-001"
    assert answer.citations[0].section == "Paid Parental Leave"
    assert answer.llm_model == "deterministic-api-test-double"
    assert llm_provider.call_count == calls_before + 1


def test_unsupported_policy_question_abstains_without_llm(
    api_dependencies: tuple[_ApiClient, DeterministicLLMProvider],
) -> None:
    client, llm_provider = api_dependencies
    calls_before = llm_provider.call_count

    response = client.post(
        "/api/v1/questions",
        json={"question": ("What is the company's annual dental implant allowance?")},
    )

    assert response.status_code == 200

    answer = WorkflowAnswer.model_validate_json(response.text)

    assert answer.route == "policy_rag"
    assert answer.abstained is True
    assert answer.citations == []
    assert answer.llm_model is None
    assert "sufficient evidence" in answer.answer.lower()
    assert llm_provider.call_count == calls_before


def test_approved_analytics_question_returns_verified_result(
    api_dependencies: tuple[_ApiClient, DeterministicLLMProvider],
) -> None:
    client, llm_provider = api_dependencies
    calls_before = llm_provider.call_count

    response = client.post(
        "/api/v1/questions",
        json={"question": APPROVED_ENGINEERING_QUESTION},
    )

    assert response.status_code == 200

    answer = WorkflowAnswer.model_validate_json(response.text)

    assert answer.route == "text_to_sql"
    assert "4 paid expense reports" in answer.answer
    assert "$3,250.00" in answer.answer
    assert answer.sql is not None
    assert answer.sql.endswith("LIMIT 100")
    assert answer.rows[0]["department"] == "Engineering"
    assert llm_provider.call_count == calls_before + 1


def test_incomplete_analytics_question_returns_clarification_without_llm(
    api_dependencies: tuple[_ApiClient, DeterministicLLMProvider],
) -> None:
    client, llm_provider = api_dependencies
    calls_before = llm_provider.call_count

    response = client.post(
        "/api/v1/questions",
        json={"question": "How much did Sales spend?"},
    )

    assert response.status_code == 200

    answer = WorkflowAnswer.model_validate_json(response.text)

    assert answer.route == "clarification"
    assert "department" in answer.answer
    assert answer.sql is None
    assert answer.llm_model is None
    assert llm_provider.call_count == calls_before


def test_destructive_request_returns_refusal_without_llm(
    api_dependencies: tuple[_ApiClient, DeterministicLLMProvider],
) -> None:
    client, llm_provider = api_dependencies
    calls_before = llm_provider.call_count

    response = client.post(
        "/api/v1/questions",
        json={"question": DESTRUCTIVE_REQUEST},
    )

    assert response.status_code == 200

    answer = WorkflowAnswer.model_validate_json(response.text)

    assert answer.route == "refusal"
    assert "read-only" in answer.answer
    assert answer.sql is None
    assert answer.llm_model is None
    assert llm_provider.call_count == calls_before

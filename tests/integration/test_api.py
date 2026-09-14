from collections.abc import Iterator, Mapping
from pathlib import Path
from typing import Any, Protocol, cast

import httpx
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine

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
from enterprise_knowledge_analytics_agent.rag.domain import RagAnswer
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

pytestmark = pytest.mark.integration

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
DOC_001_PATH = REPOSITORY_ROOT / "data" / "documents" / "DOC-001-parental-leave-policy.md"


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
    """Predictable LLM replacement used at the FastAPI boundary."""

    def __init__(self) -> None:
        self.call_count = 0

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        response_format: Mapping[str, Any],
    ) -> GenerationResult:
        self.call_count += 1

        assert "untrusted data" in system_prompt
        assert "12 weeks" in user_prompt
        assert response_format["type"] == "object"

        return GenerationResult(
            content=(
                '{"answer":"Eligible employees may receive up to '
                '12 weeks of paid parental leave.",'
                '"citation_ranks":[1]}'
            ),
            model="deterministic-api-test-double",
            prompt_tokens=100,
            completion_tokens=20,
            latency_ms=1.0,
        )


@pytest.fixture(scope="module")
def api_dependencies() -> Iterator[tuple[_ApiClient, DeterministicLLMProvider]]:
    """Prepare the real retrieval path with a deterministic LLM."""

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


def test_supported_question_crosses_api_and_returns_citation(
    api_dependencies: tuple[
        _ApiClient,
        DeterministicLLMProvider,
    ],
) -> None:
    client, llm_provider = api_dependencies
    calls_before = llm_provider.call_count

    response = client.post(
        "/api/v1/questions",
        json={"question": ("How many weeks of paid parental leave are available?")},
    )

    assert response.status_code == 200

    answer = RagAnswer.model_validate_json(response.text)

    assert answer.abstained is False
    assert "12 weeks" in answer.answer
    assert len(answer.citations) == 1
    assert answer.citations[0].document_id == "DOC-001"
    assert answer.citations[0].section == "Paid Parental Leave"
    assert answer.llm_model == "deterministic-api-test-double"
    assert llm_provider.call_count == calls_before + 1


def test_unsupported_question_crosses_api_and_skips_llm(
    api_dependencies: tuple[
        _ApiClient,
        DeterministicLLMProvider,
    ],
) -> None:
    client, llm_provider = api_dependencies
    calls_before = llm_provider.call_count

    response = client.post(
        "/api/v1/questions",
        json={"question": ("What is the company's annual dental implant allowance?")},
    )

    assert response.status_code == 200

    answer = RagAnswer.model_validate_json(response.text)

    assert answer.abstained is True
    assert answer.citations == []
    assert answer.llm_model is None
    assert "sufficient evidence" in answer.answer.lower()
    assert llm_provider.call_count == calls_before

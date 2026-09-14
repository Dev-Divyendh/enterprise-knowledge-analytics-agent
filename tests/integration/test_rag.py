from collections.abc import Iterator, Mapping
from pathlib import Path
from typing import Any

import pytest
from sqlalchemy import Engine

from enterprise_knowledge_analytics_agent.ingestion.service import ingest_markdown
from enterprise_knowledge_analytics_agent.persistence.database import (
    create_database_engine,
)
from enterprise_knowledge_analytics_agent.rag.providers import GenerationResult
from enterprise_knowledge_analytics_agent.rag.service import answer_question
from enterprise_knowledge_analytics_agent.retrieval.dense import (
    embed_document_chunks,
)
from enterprise_knowledge_analytics_agent.retrieval.embeddings import (
    SentenceTransformerEmbeddingProvider,
)

pytestmark = pytest.mark.integration

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
DOC_001_PATH = REPOSITORY_ROOT / "data" / "documents" / "DOC-001-parental-leave-policy.md"


class DeterministicLLMProvider:
    """Predictable test double that does not call a real LLM."""

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
            model="deterministic-test-double",
            prompt_tokens=100,
            completion_tokens=20,
            latency_ms=1.0,
        )


@pytest.fixture(scope="module")
def rag_dependencies() -> Iterator[tuple[Engine, SentenceTransformerEmbeddingProvider]]:
    engine = create_database_engine()
    embedding_provider = SentenceTransformerEmbeddingProvider()

    ingest_markdown(DOC_001_PATH, engine)
    embed_document_chunks(
        external_id="DOC-001",
        provider=embedding_provider,
        engine=engine,
    )

    yield engine, embedding_provider
    engine.dispose()


def test_supported_question_returns_grounded_citation(
    rag_dependencies: tuple[
        Engine,
        SentenceTransformerEmbeddingProvider,
    ],
) -> None:
    engine, embedding_provider = rag_dependencies
    llm_provider = DeterministicLLMProvider()

    answer = answer_question(
        question="How many weeks of paid parental leave are available?",
        llm_provider=llm_provider,
        embedding_provider=embedding_provider,
        engine=engine,
    )

    assert answer.abstained is False
    assert "12 weeks" in answer.answer
    assert answer.citations[0].document_id == "DOC-001"
    assert answer.citations[0].section == "Paid Parental Leave"
    assert llm_provider.call_count == 1


def test_unsupported_question_abstains_without_calling_llm(
    rag_dependencies: tuple[
        Engine,
        SentenceTransformerEmbeddingProvider,
    ],
) -> None:
    engine, embedding_provider = rag_dependencies
    llm_provider = DeterministicLLMProvider()

    answer = answer_question(
        question="What is the company's annual dental implant allowance?",
        llm_provider=llm_provider,
        embedding_provider=embedding_provider,
        engine=engine,
    )

    assert answer.abstained is True
    assert answer.citations == []
    assert "sufficient evidence" in answer.answer.lower()
    assert llm_provider.call_count == 0

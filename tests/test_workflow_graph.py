from typing import cast

import pytest
from sqlalchemy import Engine

from enterprise_knowledge_analytics_agent.analytics.service import (
    AMBIGUOUS_QUARTER_QUESTION,
    DESTRUCTIVE_REQUEST,
    RESTRICTED_DATA_REQUEST,
)
from enterprise_knowledge_analytics_agent.persistence.database import (
    create_database_engine,
)
from enterprise_knowledge_analytics_agent.rag.providers import LLMProvider
from enterprise_knowledge_analytics_agent.retrieval.embeddings import (
    EmbeddingProvider,
)
from enterprise_knowledge_analytics_agent.workflow.graph import run_workflow


@pytest.fixture
def workflow_dependencies() -> tuple[
    Engine,
    LLMProvider,
    EmbeddingProvider,
]:
    engine = create_database_engine()
    llm_provider = cast(LLMProvider, object())
    embedding_provider = cast(EmbeddingProvider, object())

    return engine, llm_provider, embedding_provider


def test_clarification_route_skips_model_and_database_dependencies(
    workflow_dependencies: tuple[
        Engine,
        LLMProvider,
        EmbeddingProvider,
    ],
) -> None:
    engine, llm_provider, embedding_provider = workflow_dependencies

    try:
        answer = run_workflow(
            AMBIGUOUS_QUARTER_QUESTION,
            llm_provider=llm_provider,
            embedding_provider=embedding_provider,
            engine=engine,
        )
    finally:
        engine.dispose()

    assert answer.route == "clarification"
    assert "quarter or exact reporting dates" in answer.answer
    assert answer.sql is None
    assert answer.citations == []
    assert answer.llm_model is None
    assert answer.total_latency_ms is not None


@pytest.mark.parametrize(
    ("question", "expected_text"),
    [
        (
            DESTRUCTIVE_REQUEST,
            "read-only",
        ),
        (
            RESTRICTED_DATA_REQUEST,
            "employee-level merchant activity",
        ),
        (
            "DROP TABLE analytics.expense_items",
            "read-only",
        ),
    ],
)
def test_refusal_route_skips_model_and_database_dependencies(
    question: str,
    expected_text: str,
    workflow_dependencies: tuple[
        Engine,
        LLMProvider,
        EmbeddingProvider,
    ],
) -> None:
    engine, llm_provider, embedding_provider = workflow_dependencies

    try:
        answer = run_workflow(
            question,
            llm_provider=llm_provider,
            embedding_provider=embedding_provider,
            engine=engine,
        )
    finally:
        engine.dispose()

    assert answer.route == "refusal"
    assert expected_text in answer.answer
    assert answer.sql is None
    assert answer.rows == []
    assert answer.citations == []
    assert answer.llm_model is None
    assert answer.total_latency_ms is not None


def test_empty_workflow_question_is_rejected(
    workflow_dependencies: tuple[
        Engine,
        LLMProvider,
        EmbeddingProvider,
    ],
) -> None:
    engine, llm_provider, embedding_provider = workflow_dependencies

    try:
        with pytest.raises(ValueError, match="must not be empty"):
            run_workflow(
                "   ",
                llm_provider=llm_provider,
                embedding_provider=embedding_provider,
                engine=engine,
            )
    finally:
        engine.dispose()

from collections.abc import Mapping
from typing import Any

import pytest

from enterprise_knowledge_analytics_agent.analytics.service import (
    AMBIGUOUS_EXPENSE_QUESTION,
    AMBIGUOUS_QUARTER_QUESTION,
    DESTRUCTIVE_REQUEST,
    RESTRICTED_DATA_REQUEST,
    answer_analytics_question,
)
from enterprise_knowledge_analytics_agent.persistence.database import (
    create_database_engine,
)
from enterprise_knowledge_analytics_agent.rag.providers import GenerationResult


class NoCallLLMProvider:
    """Fail immediately if a non-executing route calls the LLM."""

    def __init__(self) -> None:
        self.call_count = 0

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        response_format: Mapping[str, Any],
    ) -> GenerationResult:
        self.call_count += 1
        raise AssertionError("LLM must not be called for this route")


@pytest.mark.parametrize(
    ("question", "expected_text"),
    [
        (
            AMBIGUOUS_QUARTER_QUESTION,
            "quarter or exact reporting dates",
        ),
        (
            AMBIGUOUS_EXPENSE_QUESTION,
            "metric, grouping, report status",
        ),
        (
            "How much did a department spend?",
            "approved aggregate expense question",
        ),
    ],
)
def test_ambiguous_questions_request_clarification_without_llm(
    question: str,
    expected_text: str,
) -> None:
    engine = create_database_engine()
    provider = NoCallLLMProvider()

    try:
        answer = answer_analytics_question(
            question,
            llm_provider=provider,
            engine=engine,
        )
    finally:
        engine.dispose()

    assert answer.status == "clarification"
    assert expected_text in answer.answer
    assert answer.sql is None
    assert answer.rows == []
    assert answer.llm_model is None
    assert answer.prompt_tokens is None
    assert answer.completion_tokens is None
    assert provider.call_count == 0


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
    ],
)
def test_prohibited_questions_are_refused_without_llm(
    question: str,
    expected_text: str,
) -> None:
    engine = create_database_engine()
    provider = NoCallLLMProvider()

    try:
        answer = answer_analytics_question(
            question,
            llm_provider=provider,
            engine=engine,
        )
    finally:
        engine.dispose()

    assert answer.status == "refusal"
    assert expected_text in answer.answer
    assert answer.sql is None
    assert answer.rows == []
    assert answer.llm_model is None
    assert answer.prompt_tokens is None
    assert answer.completion_tokens is None
    assert provider.call_count == 0


def test_empty_analytics_question_is_rejected() -> None:
    engine = create_database_engine()
    provider = NoCallLLMProvider()

    try:
        with pytest.raises(ValueError, match="must not be empty"):
            answer_analytics_question(
                "   ",
                llm_provider=provider,
                engine=engine,
            )
    finally:
        engine.dispose()

    assert provider.call_count == 0

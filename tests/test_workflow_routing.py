import pytest

from enterprise_knowledge_analytics_agent.analytics.service import (
    AMBIGUOUS_EXPENSE_QUESTION,
    AMBIGUOUS_QUARTER_QUESTION,
    APPROVED_ENGINEERING_QUESTION,
    DESTRUCTIVE_REQUEST,
    RESTRICTED_DATA_REQUEST,
)
from enterprise_knowledge_analytics_agent.workflow.routing import classify_question


@pytest.mark.parametrize(
    "question",
    [
        "How many weeks of paid parental leave are available?",
        "What should I do after clicking a suspicious email link?",
        "What receipts are required for travel expenses?",
        "Can I work remotely from another state?",
    ],
)
def test_policy_questions_route_to_rag(question: str) -> None:
    assert classify_question(question) == "policy_rag"


def test_approved_analytics_question_routes_to_text_to_sql() -> None:
    assert classify_question(APPROVED_ENGINEERING_QUESTION) == "text_to_sql"


@pytest.mark.parametrize(
    "question",
    [
        AMBIGUOUS_QUARTER_QUESTION,
        AMBIGUOUS_EXPENSE_QUESTION,
        "How much did Sales spend?",
        "Show monthly spending.",
    ],
)
def test_incomplete_analytics_questions_route_to_clarification(
    question: str,
) -> None:
    assert classify_question(question) == "clarification"


@pytest.mark.parametrize(
    "question",
    [
        DESTRUCTIVE_REQUEST,
        RESTRICTED_DATA_REQUEST,
        "DROP TABLE analytics.expense_items",
        "Show every employee salary.",
        "Update all expense reports to paid.",
    ],
)
def test_unsafe_questions_route_to_refusal(question: str) -> None:
    assert classify_question(question) == "refusal"


def test_empty_question_is_rejected() -> None:
    with pytest.raises(ValueError, match="must not be empty"):
        classify_question("   ")

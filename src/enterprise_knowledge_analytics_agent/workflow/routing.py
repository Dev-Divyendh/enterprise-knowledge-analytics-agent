import re

from enterprise_knowledge_analytics_agent.analytics.service import (
    AMBIGUOUS_EXPENSE_QUESTION,
    AMBIGUOUS_QUARTER_QUESTION,
    APPROVED_ENGINEERING_QUESTION,
    DESTRUCTIVE_REQUEST,
    RESTRICTED_DATA_REQUEST,
)
from enterprise_knowledge_analytics_agent.workflow.domain import WorkflowRoute

DESTRUCTIVE_PATTERN = re.compile(
    r"\b(delete|drop|truncate|update|insert|alter|merge|remove)\b",
    flags=re.IGNORECASE,
)

RESTRICTED_PATTERN = re.compile(
    r"\b(salary|salaries|annual_salary|work_email|employee-level)\b",
    flags=re.IGNORECASE,
)

ANALYTICS_PATTERN = re.compile(
    r"\b("
    r"how much|"
    r"total|"
    r"average|"
    r"count|"
    r"highest|"
    r"lowest|"
    r"rank|"
    r"ranking|"
    r"monthly|"
    r"quarter|"
    r"spend|"
    r"spending"
    r")\b",
    flags=re.IGNORECASE,
)


def classify_question(question: str) -> WorkflowRoute:
    """Classify one question using deterministic application policy."""

    normalized_question = " ".join(question.split())

    if not normalized_question:
        raise ValueError("question must not be empty")

    if (
        normalized_question == DESTRUCTIVE_REQUEST
        or DESTRUCTIVE_PATTERN.search(normalized_question) is not None
    ):
        return "refusal"

    restricted_employee_merchant_request = (
        "employee" in normalized_question.lower() and "merchant" in normalized_question.lower()
    )

    if (
        normalized_question == RESTRICTED_DATA_REQUEST
        or RESTRICTED_PATTERN.search(normalized_question) is not None
        or restricted_employee_merchant_request
    ):
        return "refusal"

    if normalized_question == APPROVED_ENGINEERING_QUESTION:
        return "text_to_sql"

    if normalized_question in {
        AMBIGUOUS_QUARTER_QUESTION,
        AMBIGUOUS_EXPENSE_QUESTION,
    }:
        return "clarification"

    if ANALYTICS_PATTERN.search(normalized_question) is not None:
        return "clarification"

    return "policy_rag"

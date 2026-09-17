from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from enterprise_knowledge_analytics_agent.rag.domain import Citation

WorkflowRoute = Literal[
    "policy_rag",
    "text_to_sql",
    "clarification",
    "refusal",
]


def _empty_citations() -> list[Citation]:
    """Create a typed empty citation collection."""

    return []


def _empty_rows() -> list[dict[str, Any]]:
    """Create a typed empty analytics result set."""

    return []


class WorkflowAnswer(BaseModel):
    """Unified response returned by the controlled workflow."""

    model_config = ConfigDict(extra="forbid")

    route: WorkflowRoute
    answer: str = Field(min_length=1)
    abstained: bool = False
    citations: list[Citation] = Field(default_factory=_empty_citations)
    sql: str | None = None
    rows: list[dict[str, Any]] = Field(default_factory=_empty_rows)
    retrieval_top_score: float | None = None
    llm_model: str | None = None
    prompt_tokens: int | None = Field(default=None, ge=0)
    completion_tokens: int | None = Field(default=None, ge=0)
    total_latency_ms: float | None = Field(default=None, ge=0)

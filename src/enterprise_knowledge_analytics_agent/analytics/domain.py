from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


def _empty_rows() -> list[dict[str, Any]]:
    """Create a correctly typed empty analytics result set."""

    return []


class StrictModel(BaseModel):
    """Reject unexpected fields in structured analytics output."""

    model_config = ConfigDict(extra="forbid")


class SQLProposal(StrictModel):
    """Structured SQL proposed by an LLM."""

    sql: str = Field(min_length=1)


class AnalyticsAnswer(StrictModel):
    """Verified response returned by the analytics workflow."""

    status: Literal["answered", "clarification", "refusal"]
    answer: str = Field(min_length=1)
    sql: str | None = None
    # rows: list[dict[str, Any]] = Field(default_factory=list)
    rows: list[dict[str, Any]] = Field(default_factory=_empty_rows)
    llm_model: str | None = None
    prompt_tokens: int | None = Field(default=None, ge=0)
    completion_tokens: int | None = Field(default=None, ge=0)
    total_latency_ms: float | None = Field(default=None, ge=0)

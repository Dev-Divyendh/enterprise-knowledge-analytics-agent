from datetime import date
from enum import StrEnum
from pathlib import Path
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ExpectedRoute(StrEnum):
    POLICY_RAG = "policy_rag"
    TEXT_TO_SQL = "text_to_sql"
    CLARIFICATION = "clarification"
    REFUSAL = "refusal"


class GoldenCase(BaseModel):
    """One expected system behavior in the golden dataset."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(pattern=r"^[A-Z]{3}-\d{3}$")
    category: str = Field(min_length=1)
    difficulty: Literal["easy", "medium", "hard"]
    query: str = Field(min_length=1)
    expected_route: ExpectedRoute
    expected_behavior: str = Field(min_length=1)

    relevant_sources: list[str] = Field(default_factory=list)
    relevant_sections: list[str] = Field(default_factory=list)
    required_facts: list[str] = Field(default_factory=list)
    forbidden_claims: list[str] = Field(default_factory=list)

    required_tables: list[str] = Field(default_factory=list)
    expected_result_reference: str | None = None
    forbidden_sql_operations: list[str] = Field(default_factory=list)

    clarification_reason: str | None = None
    required_clarification: str | None = None

    refusal_reason: str | None = None
    restricted_fields: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_route_requirements(self) -> Self:
        if self.expected_route is ExpectedRoute.TEXT_TO_SQL:
            if not self.required_tables:
                raise ValueError("text_to_sql cases require at least one table")
            if self.expected_result_reference is None:
                raise ValueError("text_to_sql cases require an expected result reference")

        if self.expected_route is ExpectedRoute.CLARIFICATION:
            if self.clarification_reason is None or self.required_clarification is None:
                raise ValueError("clarification cases require reason and requested clarification")

        if self.expected_route is ExpectedRoute.REFUSAL and self.refusal_reason is None:
            raise ValueError("refusal cases require a refusal reason")

        if self.relevant_sections and (len(self.relevant_sections) != len(self.relevant_sources)):
            raise ValueError("relevant sections must align one-to-one with relevant sources")

        return self


class GoldenDataset(BaseModel):
    """Versioned collection of expected enterprise-agent behaviors."""

    model_config = ConfigDict(extra="forbid")

    dataset_name: str = Field(min_length=1)
    dataset_version: str = Field(pattern=r"^\d+\.\d+\.\d+$")
    status: Literal["specification_only", "frozen", "retired"]
    created_at: date
    description: str = Field(min_length=1)
    cases: list[GoldenCase] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_unique_case_ids(self) -> Self:
        case_ids = [case.id for case in self.cases]

        if len(case_ids) != len(set(case_ids)):
            raise ValueError("golden dataset contains duplicate case IDs")

        return self


def load_golden_dataset(path: Path) -> GoldenDataset:
    """Read and validate a golden dataset from JSON."""

    return GoldenDataset.model_validate_json(path.read_text(encoding="utf-8"))

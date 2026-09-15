import json
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from enterprise_knowledge_analytics_agent.evaluation.golden import (
    ExpectedRoute,
    GoldenCase,
    load_golden_dataset,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
GOLDEN_DATASET_PATH = PROJECT_ROOT / "data/golden/v0.1/cases.json"


def read_raw_dataset() -> dict[str, Any]:
    return json.loads(GOLDEN_DATASET_PATH.read_text(encoding="utf-8"))


def test_load_golden_dataset() -> None:
    dataset = load_golden_dataset(GOLDEN_DATASET_PATH)

    assert dataset.dataset_version == "0.1.0"
    assert dataset.status == "specification_only"
    assert len(dataset.cases) == 15


def test_dataset_contains_all_routes() -> None:
    dataset = load_golden_dataset(GOLDEN_DATASET_PATH)
    routes = {case.expected_route for case in dataset.cases}

    assert routes == set(ExpectedRoute)


def test_duplicate_case_ids_are_rejected(tmp_path: Path) -> None:
    raw_dataset = read_raw_dataset()
    raw_dataset["cases"].append(raw_dataset["cases"][0])

    invalid_path = tmp_path / "duplicate-cases.json"
    invalid_path.write_text(json.dumps(raw_dataset), encoding="utf-8")

    with pytest.raises(ValidationError, match="duplicate case IDs"):
        load_golden_dataset(invalid_path)


def test_text_to_sql_case_requires_result_reference(tmp_path: Path) -> None:
    raw_dataset = read_raw_dataset()
    sql_case = next(
        case for case in raw_dataset["cases"] if case["expected_route"] == "text_to_sql"
    )
    sql_case.pop("expected_result_reference")

    invalid_path = tmp_path / "invalid-sql-case.json"
    invalid_path.write_text(json.dumps(raw_dataset), encoding="utf-8")

    with pytest.raises(ValidationError, match="expected result reference"):
        load_golden_dataset(invalid_path)


def test_relevant_sections_must_align_with_sources() -> None:
    with pytest.raises(
        ValueError,
        match="relevant sections must align",
    ):
        GoldenCase(
            id="KNO-999",
            category="direct_policy",
            difficulty="easy",
            query="Test question",
            expected_route=ExpectedRoute.POLICY_RAG,
            relevant_sources=["DOC-001"],
            relevant_sections=["Section One", "Section Two"],
            required_facts=[],
            forbidden_claims=[],
            expected_behavior="answer_with_citations",
        )

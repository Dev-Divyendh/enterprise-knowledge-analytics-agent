from collections.abc import Sequence
from math import ceil
from time import perf_counter
from typing import Protocol

from pydantic import BaseModel, ConfigDict, Field

from enterprise_knowledge_analytics_agent.evaluation.golden import (
    GoldenCase,
    GoldenDataset,
)
from enterprise_knowledge_analytics_agent.retrieval.dense import RetrievedChunk


class RetrievalFunction(Protocol):
    """Retrieval behavior required by the evaluation runner."""

    def __call__(
        self,
        question: str,
        top_k: int,
    ) -> list[RetrievedChunk]:
        """Return ranked chunks for one question."""

        ...


class RetrievedEvidence(BaseModel):
    """Serializable representation of one retrieved chunk."""

    model_config = ConfigDict(extra="forbid")

    rank: int
    document_id: str
    section: str
    chunk_id: str
    similarity_score: float
    relevant: bool


class RetrievalCaseResult(BaseModel):
    """Measured retrieval behavior for one golden case."""

    model_config = ConfigDict(extra="forbid")

    case_id: str
    category: str
    query: str
    answerable: bool
    expected_evidence: list[str]
    retrieved_evidence: list[RetrievedEvidence]
    hit: bool | None
    recall: float | None
    precision: float | None
    reciprocal_rank: float | None
    top_similarity_score: float | None
    latency_ms: float


class RetrievalMetrics(BaseModel):
    """Aggregate metrics for answerable retrieval cases."""

    model_config = ConfigDict(extra="forbid")

    evaluated_cases: int
    answerable_cases: int
    unsupported_cases: int
    hit_rate_at_k: float
    recall_at_k: float
    precision_at_k: float
    mean_reciprocal_rank: float
    latency_p50_ms: float
    latency_p95_ms: float
    unsupported_top_score_min: float | None
    unsupported_top_score_max: float | None
    unsupported_top_score_mean: float | None


class RetrievalEvaluationReport(BaseModel):
    """Versioned result of one retrieval evaluation run."""

    model_config = ConfigDict(extra="forbid")

    dataset_name: str
    dataset_version: str
    retrieval_system: str
    top_k: int = Field(ge=1)
    metrics: RetrievalMetrics
    cases: list[RetrievalCaseResult]


def _evidence_key(document_id: str, section: str) -> str:
    return f"{document_id}::{section}"


def _expected_evidence(case: GoldenCase) -> list[str]:
    return [
        _evidence_key(document_id, section)
        for document_id, section in zip(
            case.relevant_sources,
            case.relevant_sections,
            strict=True,
        )
    ]


def _percentile(values: Sequence[float], percentile: float) -> float:
    """Calculate a nearest-rank percentile for a non-empty sequence."""

    if not values:
        raise ValueError("percentile requires at least one value")

    ordered_values = sorted(values)
    index = max(ceil(percentile * len(ordered_values)) - 1, 0)

    return ordered_values[index]


def _mean(values: Sequence[float]) -> float:
    if not values:
        return 0.0

    return sum(values) / len(values)


def evaluate_retrieval(
    dataset: GoldenDataset,
    retriever: RetrievalFunction,
    *,
    retrieval_system: str,
    top_k: int = 5,
) -> RetrievalEvaluationReport:
    """Evaluate one retrieval implementation against a frozen dataset."""

    if dataset.status != "frozen":
        raise ValueError("retrieval evaluation requires a frozen dataset")

    if top_k < 1:
        raise ValueError("top_k must be at least 1")

    case_results: list[RetrievalCaseResult] = []

    for case in dataset.cases:
        expected_evidence = _expected_evidence(case)
        expected_set = set(expected_evidence)
        answerable = bool(expected_set)

        started_at = perf_counter()
        retrieved_chunks = retriever(case.query, top_k)
        latency_ms = round((perf_counter() - started_at) * 1000, 3)

        retrieved_evidence: list[RetrievedEvidence] = []
        retrieved_keys: list[str] = []

        for chunk in retrieved_chunks:
            evidence_key = _evidence_key(
                chunk.document_id,
                chunk.section,
            )
            retrieved_keys.append(evidence_key)
            retrieved_evidence.append(
                RetrievedEvidence(
                    rank=chunk.rank,
                    document_id=chunk.document_id,
                    section=chunk.section,
                    chunk_id=chunk.chunk_id,
                    similarity_score=chunk.similarity_score,
                    relevant=evidence_key in expected_set,
                )
            )

        top_similarity_score = retrieved_chunks[0].similarity_score if retrieved_chunks else None

        if answerable:
            distinct_matches = expected_set.intersection(retrieved_keys)
            relevant_result_count = sum(
                evidence_key in expected_set for evidence_key in retrieved_keys
            )
            first_relevant_rank = next(
                (
                    index
                    for index, evidence_key in enumerate(
                        retrieved_keys,
                        start=1,
                    )
                    if evidence_key in expected_set
                ),
                None,
            )

            hit: bool | None = bool(distinct_matches)
            recall: float | None = len(distinct_matches) / len(expected_set)
            precision: float | None = (
                relevant_result_count / len(retrieved_keys) if retrieved_keys else 0.0
            )
            reciprocal_rank: float | None = (
                1.0 / first_relevant_rank if first_relevant_rank is not None else 0.0
            )
        else:
            hit = None
            recall = None
            precision = None
            reciprocal_rank = None

        case_results.append(
            RetrievalCaseResult(
                case_id=case.id,
                category=case.category,
                query=case.query,
                answerable=answerable,
                expected_evidence=expected_evidence,
                retrieved_evidence=retrieved_evidence,
                hit=hit,
                recall=recall,
                precision=precision,
                reciprocal_rank=reciprocal_rank,
                top_similarity_score=top_similarity_score,
                latency_ms=latency_ms,
            )
        )

    answerable_results = [result for result in case_results if result.answerable]
    unsupported_results = [result for result in case_results if not result.answerable]
    latencies = [result.latency_ms for result in case_results]
    unsupported_scores = [
        result.top_similarity_score
        for result in unsupported_results
        if result.top_similarity_score is not None
    ]

    return RetrievalEvaluationReport(
        dataset_name=dataset.dataset_name,
        dataset_version=dataset.dataset_version,
        retrieval_system=retrieval_system,
        top_k=top_k,
        metrics=RetrievalMetrics(
            evaluated_cases=len(case_results),
            answerable_cases=len(answerable_results),
            unsupported_cases=len(unsupported_results),
            hit_rate_at_k=_mean([1.0 if result.hit else 0.0 for result in answerable_results]),
            recall_at_k=_mean(
                [result.recall for result in answerable_results if result.recall is not None]
            ),
            precision_at_k=_mean(
                [result.precision for result in answerable_results if result.precision is not None]
            ),
            mean_reciprocal_rank=_mean(
                [
                    result.reciprocal_rank
                    for result in answerable_results
                    if result.reciprocal_rank is not None
                ]
            ),
            latency_p50_ms=(_percentile(latencies, 0.50) if latencies else 0.0),
            latency_p95_ms=(_percentile(latencies, 0.95) if latencies else 0.0),
            unsupported_top_score_min=(min(unsupported_scores) if unsupported_scores else None),
            unsupported_top_score_max=(max(unsupported_scores) if unsupported_scores else None),
            unsupported_top_score_mean=(_mean(unsupported_scores) if unsupported_scores else None),
        ),
        cases=case_results,
    )

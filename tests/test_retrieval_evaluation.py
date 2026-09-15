from datetime import date

from enterprise_knowledge_analytics_agent.evaluation.golden import (
    ExpectedRoute,
    GoldenCase,
    GoldenDataset,
)
from enterprise_knowledge_analytics_agent.evaluation.retrieval import (
    evaluate_retrieval,
)
from enterprise_knowledge_analytics_agent.retrieval.dense import RetrievedChunk


def make_chunk(
    *,
    rank: int,
    document_id: str,
    section: str,
    score: float,
) -> RetrievedChunk:
    return RetrievedChunk(
        rank=rank,
        chunk_id=f"chunk-{rank}",
        document_id=document_id,
        document_name=f"{document_id} title",
        section=section,
        content="Evidence content",
        similarity_score=score,
    )


def make_dataset() -> GoldenDataset:
    return GoldenDataset(
        dataset_name="retrieval_test",
        dataset_version="1.0.0",
        status="frozen",
        created_at=date(2026, 9, 15),
        description="Deterministic retrieval metric test.",
        cases=[
            GoldenCase(
                id="KNO-001",
                category="direct_policy",
                difficulty="easy",
                query="Supported question",
                expected_route=ExpectedRoute.POLICY_RAG,
                relevant_sources=["DOC-001"],
                relevant_sections=["Expected Section"],
                expected_behavior="answer_with_citations",
            ),
            GoldenCase(
                id="KNO-002",
                category="unsupported_knowledge",
                difficulty="easy",
                query="Unsupported question",
                expected_route=ExpectedRoute.POLICY_RAG,
                expected_behavior="abstain",
            ),
        ],
    )


def test_evaluator_calculates_ranked_retrieval_metrics() -> None:
    def retrieve(question: str, top_k: int) -> list[RetrievedChunk]:
        assert top_k == 2

        if question == "Supported question":
            return [
                make_chunk(
                    rank=1,
                    document_id="DOC-999",
                    section="Distractor",
                    score=0.80,
                ),
                make_chunk(
                    rank=2,
                    document_id="DOC-001",
                    section="Expected Section",
                    score=0.75,
                ),
            ]

        return [
            make_chunk(
                rank=1,
                document_id="DOC-999",
                section="Distractor",
                score=0.45,
            )
        ]

    report = evaluate_retrieval(
        make_dataset(),
        retrieve,
        retrieval_system="deterministic",
        top_k=2,
    )

    assert report.metrics.evaluated_cases == 2
    assert report.metrics.answerable_cases == 1
    assert report.metrics.unsupported_cases == 1
    assert report.metrics.hit_rate_at_k == 1.0
    assert report.metrics.recall_at_k == 1.0
    assert report.metrics.precision_at_k == 0.5
    assert report.metrics.mean_reciprocal_rank == 0.5
    assert report.metrics.unsupported_top_score_max == 0.45

    supported_result = report.cases[0]
    assert supported_result.hit is True
    assert supported_result.retrieved_evidence[1].relevant is True


def test_evaluator_rejects_non_frozen_dataset() -> None:
    dataset = make_dataset().model_copy(update={"status": "specification_only"})

    def retrieve(
        question: str,
        top_k: int,
    ) -> list[RetrievedChunk]:
        return []

    try:
        evaluate_retrieval(
            dataset,
            retrieve,
            retrieval_system="deterministic",
        )
    except ValueError as error:
        assert "frozen dataset" in str(error)
    else:
        raise AssertionError("non-frozen dataset should be rejected")

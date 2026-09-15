import pytest

from enterprise_knowledge_analytics_agent.retrieval.dense import RetrievedChunk
from enterprise_knowledge_analytics_agent.retrieval.hybrid import fuse_rrf


def chunk(
    chunk_id: str,
    rank: int,
    score: float,
) -> RetrievedChunk:
    return RetrievedChunk(
        rank=rank,
        chunk_id=chunk_id,
        document_id="DOC-001",
        document_name="Test Policy",
        section="Test Section",
        content="Test evidence",
        similarity_score=score,
    )


def test_rrf_promotes_chunk_present_in_both_lists() -> None:
    dense = [
        chunk("dense-only", 1, 0.95),
        chunk("shared", 2, 0.70),
    ]
    lexical = [
        chunk("shared", 1, 0.02),
        chunk("lexical-only", 2, 100.0),
    ]

    results = fuse_rrf(dense, lexical, top_k=3)

    assert [result.chunk_id for result in results] == [
        "shared",
        "dense-only",
        "lexical-only",
    ]
    assert [result.rank for result in results] == [1, 2, 3]
    assert results[0].similarity_score > results[1].similarity_score


def test_rrf_does_not_compare_incompatible_input_scores() -> None:
    dense = [chunk("dense-first", 1, 0.01)]
    lexical = [chunk("lexical-first", 1, 999.0)]

    results = fuse_rrf(dense, lexical, top_k=2)

    # Equal rank contributions tie; chunk ID provides stable ordering.
    assert [result.chunk_id for result in results] == [
        "dense-first",
        "lexical-first",
    ]
    assert results[0].similarity_score == results[1].similarity_score


def test_rrf_rejects_invalid_parameters() -> None:
    with pytest.raises(ValueError, match="top_k"):
        fuse_rrf([], [], top_k=0)

    with pytest.raises(ValueError, match="rrf_k"):
        fuse_rrf([], [], rrf_k=0)

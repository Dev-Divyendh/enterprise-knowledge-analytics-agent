from dataclasses import replace

from sqlalchemy import Engine

from enterprise_knowledge_analytics_agent.persistence.database import (
    create_database_engine,
)
from enterprise_knowledge_analytics_agent.retrieval.dense import (
    RetrievedChunk,
    retrieve_dense,
)
from enterprise_knowledge_analytics_agent.retrieval.embeddings import (
    EmbeddingProvider,
    SentenceTransformerEmbeddingProvider,
)
from enterprise_knowledge_analytics_agent.retrieval.lexical import retrieve_lexical

DEFAULT_RRF_K = 60
DEFAULT_CANDIDATE_K = 10


def fuse_rrf(
    dense_results: list[RetrievedChunk],
    lexical_results: list[RetrievedChunk],
    *,
    top_k: int = 3,
    rrf_k: int = DEFAULT_RRF_K,
) -> list[RetrievedChunk]:
    """Fuse two ranked chunk lists without comparing their score scales."""

    if top_k < 1:
        raise ValueError("top_k must be at least 1")

    if rrf_k < 1:
        raise ValueError("rrf_k must be at least 1")

    chunks_by_id: dict[str, RetrievedChunk] = {}
    fused_scores: dict[str, float] = {}

    for results in (dense_results, lexical_results):
        seen_in_list: set[str] = set()

        for position, chunk in enumerate(results, start=1):
            if chunk.chunk_id in seen_in_list:
                continue

            seen_in_list.add(chunk.chunk_id)
            chunks_by_id.setdefault(chunk.chunk_id, chunk)
            fused_scores[chunk.chunk_id] = fused_scores.get(chunk.chunk_id, 0.0) + 1.0 / (
                rrf_k + position
            )

    ranked_ids = sorted(
        fused_scores,
        key=lambda chunk_id: (
            -fused_scores[chunk_id],
            chunk_id,
        ),
    )

    return [
        replace(
            chunks_by_id[chunk_id],
            rank=rank,
            # This is an RRF score, NOT cosine similarity.
            similarity_score=round(fused_scores[chunk_id], 9),
        )
        for rank, chunk_id in enumerate(ranked_ids[:top_k], start=1)
    ]


def retrieve_hybrid(
    question: str,
    *,
    top_k: int = 3,
    candidate_k: int = DEFAULT_CANDIDATE_K,
    rrf_k: int = DEFAULT_RRF_K,
    provider: EmbeddingProvider | None = None,
    engine: Engine | None = None,
) -> list[RetrievedChunk]:
    """Run exact dense and lexical search, then fuse their rankings."""

    if top_k < 1:
        raise ValueError("top_k must be at least 1")

    if candidate_k < top_k:
        raise ValueError("candidate_k must be at least top_k")

    resolved_engine = engine or create_database_engine()
    owns_engine = engine is None

    try:
        resolved_provider = provider or SentenceTransformerEmbeddingProvider()

        dense_results = retrieve_dense(
            question,
            top_k=candidate_k,
            provider=resolved_provider,
            engine=resolved_engine,
        )
        lexical_results = retrieve_lexical(
            question,
            top_k=candidate_k,
            engine=resolved_engine,
        )

        return fuse_rrf(
            dense_results,
            lexical_results,
            top_k=top_k,
            rrf_k=rrf_k,
        )
    finally:
        if owns_engine:
            resolved_engine.dispose()

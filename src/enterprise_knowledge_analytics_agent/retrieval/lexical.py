import re

from sqlalchemy import Engine, func, select
from sqlalchemy.orm import Session

from enterprise_knowledge_analytics_agent.persistence.database import (
    create_database_engine,
)
from enterprise_knowledge_analytics_agent.persistence.models import (
    Chunk,
    Document,
    DocumentVersion,
)
from enterprise_knowledge_analytics_agent.retrieval.dense import RetrievedChunk


def retrieve_lexical(
    question: str,
    top_k: int = 3,
    engine: Engine | None = None,
) -> list[RetrievedChunk]:
    """Search active document chunks using PostgreSQL full-text ranking."""

    if top_k < 1:
        raise ValueError("top_k must be at least 1")

    normalized_question = question.strip()

    if not normalized_question:
        raise ValueError("question must not be empty")

    resolved_engine = engine or create_database_engine()
    owns_engine = engine is None

    try:
        terms = re.findall(r"[A-Za-z0-9]+", normalized_question)

        if not terms:
            return []

        query = func.websearch_to_tsquery(
            "english",
            " OR ".join(terms[:32]),
        )
        relevance = func.ts_rank_cd(Chunk.search_vector, query)

        statement = (
            select(
                Chunk.id,
                Chunk.content,
                Chunk.chunk_metadata,
                Document.external_id,
                Document.title,
                relevance.label("lexical_score"),
            )
            .join(
                DocumentVersion,
                DocumentVersion.id == Chunk.document_version_id,
            )
            .join(Document, Document.id == DocumentVersion.document_id)
            .where(
                DocumentVersion.is_active.is_(True),
                Chunk.search_vector.op("@@")(query),
            )
            .order_by(relevance.desc(), Chunk.id)
            .limit(top_k)
        )

        with Session(resolved_engine) as session:
            rows = session.execute(statement).tuples().all()

        results: list[RetrievedChunk] = []

        for rank, row in enumerate(rows, start=1):
            (
                chunk_id,
                content,
                metadata,
                external_id,
                document_title,
                lexical_score,
            ) = row

            section_value = metadata.get("section")
            section = section_value if isinstance(section_value, str) else "Unknown section"

            results.append(
                RetrievedChunk(
                    rank=rank,
                    chunk_id=chunk_id,
                    document_id=external_id or "unknown",
                    document_name=document_title,
                    section=section,
                    content=content,
                    # Existing field name is reused for ranked-output
                    # compatibility. This is NOT cosine similarity.
                    similarity_score=round(float(lexical_score), 6),
                )
            )

        return results
    finally:
        if owns_engine:
            resolved_engine.dispose()

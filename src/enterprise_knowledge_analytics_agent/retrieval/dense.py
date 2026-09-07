from dataclasses import dataclass
from time import perf_counter

from sqlalchemy import Engine, func, select
from sqlalchemy.orm import Session

from enterprise_knowledge_analytics_agent.persistence.database import (
    create_database_engine,
)
from enterprise_knowledge_analytics_agent.persistence.models import (
    Chunk,
    Document,
    DocumentVersion,
    Embedding,
)
from enterprise_knowledge_analytics_agent.retrieval.embeddings import (
    EmbeddingProvider,
    SentenceTransformerEmbeddingProvider,
)


@dataclass(frozen=True)
class EmbeddingRunResult:
    """Summary of one idempotent embedding operation."""

    external_id: str
    model_name: str
    model_version: str
    dimension: int
    chunk_count: int
    embeddings_created: int
    embeddings_already_present: int
    elapsed_ms: float


@dataclass(frozen=True)
class RetrievedChunk:
    """One ranked chunk returned by dense retrieval."""

    rank: int
    chunk_id: str
    document_id: str
    document_name: str
    section: str
    content: str
    similarity_score: float


def embed_document_chunks(
    external_id: str,
    provider: EmbeddingProvider | None = None,
    engine: Engine | None = None,
) -> EmbeddingRunResult:
    """Embed active chunks while skipping vectors already stored."""

    resolved_provider = provider or SentenceTransformerEmbeddingProvider()
    resolved_engine = engine or create_database_engine()
    owns_engine = engine is None
    started_at = perf_counter()

    try:
        with Session(resolved_engine) as session, session.begin():
            chunks = list(
                session.scalars(
                    select(Chunk)
                    .join(
                        DocumentVersion,
                        DocumentVersion.id == Chunk.document_version_id,
                    )
                    .join(
                        Document,
                        Document.id == DocumentVersion.document_id,
                    )
                    .where(
                        Document.external_id == external_id,
                        DocumentVersion.is_active.is_(True),
                    )
                    .order_by(Chunk.ordinal)
                ).all()
            )

            if not chunks:
                raise LookupError(f"no active chunks found for document {external_id}")

            existing_chunk_ids = set(
                session.scalars(
                    select(Embedding.chunk_id).where(
                        Embedding.chunk_id.in_([chunk.id for chunk in chunks]),
                        Embedding.model_name == resolved_provider.model_name,
                        Embedding.model_version == resolved_provider.model_version,
                    )
                ).all()
            )

            missing_chunks = [chunk for chunk in chunks if chunk.id not in existing_chunk_ids]

            vectors = resolved_provider.embed_documents([chunk.content for chunk in missing_chunks])

            if len(vectors) != len(missing_chunks):
                raise RuntimeError("embedding provider returned an unexpected vector count")

            generation_elapsed_ms = (perf_counter() - started_at) * 1000
            latency_per_vector = generation_elapsed_ms / len(vectors) if vectors else None

            for chunk, vector in zip(missing_chunks, vectors, strict=True):
                if len(vector) != resolved_provider.dimension:
                    raise RuntimeError("embedding vector has an unexpected dimension")

                session.add(
                    Embedding(
                        chunk_id=chunk.id,
                        model_name=resolved_provider.model_name,
                        model_version=resolved_provider.model_version,
                        dimensions=resolved_provider.dimension,
                        vector=vector,
                        normalized=True,
                        generation_latency_ms=latency_per_vector,
                    )
                )

            session.flush()

            return EmbeddingRunResult(
                external_id=external_id,
                model_name=resolved_provider.model_name,
                model_version=resolved_provider.model_version,
                dimension=resolved_provider.dimension,
                chunk_count=len(chunks),
                embeddings_created=len(missing_chunks),
                embeddings_already_present=len(existing_chunk_ids),
                elapsed_ms=round(
                    (perf_counter() - started_at) * 1000,
                    3,
                ),
            )
    finally:
        if owns_engine:
            resolved_engine.dispose()


def retrieve_dense(
    question: str,
    top_k: int = 3,
    provider: EmbeddingProvider | None = None,
    engine: Engine | None = None,
) -> list[RetrievedChunk]:
    """Retrieve active chunks using exact pgvector cosine search."""

    if top_k < 1:
        raise ValueError("top_k must be at least 1")

    resolved_provider = provider or SentenceTransformerEmbeddingProvider()
    resolved_engine = engine or create_database_engine()
    owns_engine = engine is None

    try:
        query_vector = resolved_provider.embed_query(question)
        distance = Embedding.vector.cosine_distance(query_vector)

        statement = (
            select(
                Chunk.id,
                Chunk.content,
                Chunk.chunk_metadata,
                Document.external_id,
                Document.title,
                distance.label("distance"),
            )
            .join(Embedding, Embedding.chunk_id == Chunk.id)
            .join(
                DocumentVersion,
                DocumentVersion.id == Chunk.document_version_id,
            )
            .join(Document, Document.id == DocumentVersion.document_id)
            .where(
                DocumentVersion.is_active.is_(True),
                Embedding.model_name == resolved_provider.model_name,
                Embedding.model_version == resolved_provider.model_version,
                Embedding.dimensions == resolved_provider.dimension,
            )
            .order_by(distance)
            .limit(top_k)
        )

        with Session(resolved_engine) as session:
            rows = session.execute(statement).tuples().all()

        results: list[RetrievedChunk] = []

        for rank, row in enumerate(rows, start=1):
            (
                chunk_id,
                content,
                metadata_value,
                external_id,
                document_title,
                distance_value,
            ) = row

            metadata = metadata_value
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
                    similarity_score=round(
                        1.0 - float(distance_value),
                        6,
                    ),
                )
            )

        return results
    finally:
        if owns_engine:
            resolved_engine.dispose()


def count_stored_embeddings(
    external_id: str,
    engine: Engine | None = None,
) -> int:
    """Return the number of embeddings stored for one active document."""

    resolved_engine = engine or create_database_engine()
    owns_engine = engine is None

    try:
        with Session(resolved_engine) as session:
            count = session.scalar(
                select(func.count(Embedding.id))
                .join(Chunk, Chunk.id == Embedding.chunk_id)
                .join(
                    DocumentVersion,
                    DocumentVersion.id == Chunk.document_version_id,
                )
                .join(Document, Document.id == DocumentVersion.document_id)
                .where(
                    Document.external_id == external_id,
                    DocumentVersion.is_active.is_(True),
                )
            )

        return int(count or 0)
    finally:
        if owns_engine:
            resolved_engine.dispose()

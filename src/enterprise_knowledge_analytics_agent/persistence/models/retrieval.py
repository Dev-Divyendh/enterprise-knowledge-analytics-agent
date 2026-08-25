import uuid
from datetime import datetime
from typing import Any

from pgvector.sqlalchemy import VECTOR
from sqlalchemy import (
    CheckConstraint,
    Computed,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, TSVECTOR, UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from enterprise_knowledge_analytics_agent.persistence.models.base import Base


class Chunk(Base):
    """Retrievable piece of a specific document version."""

    __tablename__ = "chunks"
    __table_args__ = (
        UniqueConstraint(
            "document_version_id",
            "ordinal",
            "chunk_version",
            name="uq_chunks_version_ordinal_chunk_version",
        ),
        CheckConstraint(
            "ordinal >= 0",
            name="ordinal_nonnegative",
        ),
        CheckConstraint(
            "chunk_version > 0",
            name="chunk_version_positive",
        ),
        CheckConstraint(
            "token_count >= 0",
            name="token_count_nonnegative",
        ),
        CheckConstraint(
            "page_start IS NULL OR page_start > 0",
            name="page_start_positive",
        ),
        CheckConstraint(
            "page_end IS NULL OR page_end > 0",
            name="page_end_positive",
        ),
        CheckConstraint(
            "page_start IS NULL OR page_end IS NULL OR page_end >= page_start",
            name="page_range_valid",
        ),
        Index(
            "ix_chunks_document_order",
            "document_version_id",
            "ordinal",
        ),
        Index(
            "ix_chunks_content_hash",
            "content_hash",
        ),
        Index(
            "ix_chunks_search_vector",
            "search_vector",
            postgresql_using="gin",
        ),
    )

    id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
    )
    document_version_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("document_versions.id", ondelete="CASCADE"),
        nullable=False,
    )
    parent_chunk_id: Mapped[str | None] = mapped_column(
        String(64),
        ForeignKey("chunks.id", ondelete="SET NULL"),
    )
    ordinal: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    chunk_version: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
    )
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    content_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )
    token_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    page_start: Mapped[int | None] = mapped_column(Integer)
    page_end: Mapped[int | None] = mapped_column(Integer)
    section_path: Mapped[list[str]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
        server_default="[]",
    )
    element_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="text",
        server_default="text",
    )
    table_data: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    chunk_metadata: Mapped[dict[str, Any]] = mapped_column(
        "metadata",
        JSONB,
        nullable=False,
        default=dict,
        server_default="{}",
    )
    access_control: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        server_default="{}",
    )
    search_vector: Mapped[Any] = mapped_column(
        TSVECTOR,
        Computed(
            "to_tsvector('english', coalesce(content, ''))",
            persisted=True,
        ),
        nullable=False,
    )


class Embedding(Base):
    """Versioned vector representation of a chunk."""

    __tablename__ = "embeddings"
    __table_args__ = (
        UniqueConstraint(
            "chunk_id",
            "model_name",
            "model_version",
            name="uq_embeddings_chunk_model_version",
        ),
        CheckConstraint("dimensions > 0", name="dimensions_positive"),
        CheckConstraint(
            "generation_latency_ms IS NULL OR generation_latency_ms >= 0",
            name="generation_latency_nonnegative",
        ),
        Index("ix_embeddings_chunk_id", "chunk_id"),
        Index("ix_embeddings_model", "model_name", "model_version"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    chunk_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("chunks.id", ondelete="CASCADE"),
        nullable=False,
    )
    model_name: Mapped[str] = mapped_column(String(255), nullable=False)
    model_version: Mapped[str] = mapped_column(String(100), nullable=False)
    dimensions: Mapped[int] = mapped_column(Integer, nullable=False)
    vector: Mapped[Any] = mapped_column(VECTOR, nullable=False)
    normalized: Mapped[bool] = mapped_column(nullable=False, default=True)
    generation_latency_ms: Mapped[float | None] = mapped_column(Float)
    embedded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

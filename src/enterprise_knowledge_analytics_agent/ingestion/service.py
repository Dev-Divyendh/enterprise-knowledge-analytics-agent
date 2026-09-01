from dataclasses import dataclass
from pathlib import Path
from typing import Literal
from uuid import UUID

from sqlalchemy import Engine, func, select, update
from sqlalchemy.orm import Session

from enterprise_knowledge_analytics_agent.ingestion.domain import CanonicalDocument
from enterprise_knowledge_analytics_agent.ingestion.markdown import (
    read_markdown_document,
)
from enterprise_knowledge_analytics_agent.persistence.database import (
    create_database_engine,
)
from enterprise_knowledge_analytics_agent.persistence.models import (
    Chunk,
    Document,
    DocumentVersion,
    SourceType,
)
from enterprise_knowledge_analytics_agent.processing.chunking import build_chunks


@dataclass(frozen=True)
class IngestionResult:
    """Observable result of ingesting and chunking one source document."""

    status: Literal["created", "unchanged"]
    document_id: UUID
    document_version_id: UUID
    external_id: str
    version_number: int
    content_hash: str
    element_count: int
    chunk_count: int


def ingest_markdown(
    path: Path,
    engine: Engine | None = None,
) -> IngestionResult:
    """Ingest and chunk Markdown without duplicating unchanged content."""

    canonical_document = read_markdown_document(path)
    resolved_engine = engine or create_database_engine()
    owns_engine = engine is None

    try:
        with Session(resolved_engine) as session, session.begin():
            document = session.scalar(
                select(Document).where(Document.source_uri == canonical_document.source_uri)
            )

            if document is None:
                external_id_value = canonical_document.metadata.get("external_id")
                external_id = external_id_value if isinstance(external_id_value, str) else None

                document = Document(
                    source_type=SourceType.LOCAL_FILESYSTEM,
                    source_uri=canonical_document.source_uri,
                    external_id=external_id,
                    title=canonical_document.title,
                    mime_type=canonical_document.mime_type,
                )
                session.add(document)
                session.flush()

            existing_version = session.scalar(
                select(DocumentVersion).where(
                    DocumentVersion.document_id == document.id,
                    DocumentVersion.content_hash == canonical_document.content_hash,
                )
            )

            external_id = document.external_id or str(document.id)

            if existing_version is not None:
                chunk_count = _persist_chunks_if_missing(
                    session=session,
                    document_version=existing_version,
                    canonical_document=canonical_document,
                )

                return IngestionResult(
                    status="unchanged",
                    document_id=document.id,
                    document_version_id=existing_version.id,
                    external_id=external_id,
                    version_number=existing_version.version_number,
                    content_hash=existing_version.content_hash,
                    element_count=len(canonical_document.elements),
                    chunk_count=chunk_count,
                )

            latest_version = session.scalar(
                select(func.coalesce(func.max(DocumentVersion.version_number), 0)).where(
                    DocumentVersion.document_id == document.id
                )
            )
            version_number = int(latest_version or 0) + 1

            session.execute(
                update(DocumentVersion)
                .where(
                    DocumentVersion.document_id == document.id,
                    DocumentVersion.is_active.is_(True),
                )
                .values(is_active=False)
            )

            document_version = DocumentVersion(
                document_id=document.id,
                version_number=version_number,
                content_hash=canonical_document.content_hash,
                file_size_bytes=canonical_document.file_size_bytes,
                is_active=True,
                parser_name=canonical_document.parser_name,
                parser_version=canonical_document.parser_version,
                source_metadata={
                    **canonical_document.metadata,
                    "canonical_elements": [
                        element.model_dump(mode="json") for element in canonical_document.elements
                    ],
                },
            )
            session.add(document_version)
            session.flush()

            chunk_count = _persist_chunks_if_missing(
                session=session,
                document_version=document_version,
                canonical_document=canonical_document,
            )

            return IngestionResult(
                status="created",
                document_id=document.id,
                document_version_id=document_version.id,
                external_id=external_id,
                version_number=document_version.version_number,
                content_hash=document_version.content_hash,
                element_count=len(canonical_document.elements),
                chunk_count=chunk_count,
            )
    finally:
        if owns_engine:
            resolved_engine.dispose()


def _persist_chunks_if_missing(
    session: Session,
    document_version: DocumentVersion,
    canonical_document: CanonicalDocument,
) -> int:
    """Create chunks once and return the stored chunk count."""

    existing_count = session.scalar(
        select(func.count(Chunk.id)).where(Chunk.document_version_id == document_version.id)
    )
    resolved_existing_count = int(existing_count or 0)

    if resolved_existing_count > 0:
        return resolved_existing_count

    drafts = build_chunks(
        document=canonical_document,
        document_version_id=document_version.id,
    )

    session.add_all(
        [
            Chunk(
                id=draft.id,
                document_version_id=document_version.id,
                parent_chunk_id=None,
                ordinal=draft.ordinal,
                chunk_version=draft.chunk_version,
                content=draft.content,
                content_hash=draft.content_hash,
                token_count=draft.token_count,
                page_start=None,
                page_end=None,
                section_path=draft.section_path,
                element_type=draft.element_type,
                table_data=None,
                chunk_metadata=draft.metadata,
                access_control={},
            )
            for draft in drafts
        ]
    )
    session.flush()

    return len(drafts)

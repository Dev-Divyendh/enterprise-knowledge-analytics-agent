from collections.abc import Iterator
from pathlib import Path

import pytest
from sqlalchemy import Engine, delete, func, select
from sqlalchemy.orm import Session

from enterprise_knowledge_analytics_agent.ingestion.service import ingest_markdown
from enterprise_knowledge_analytics_agent.persistence.database import (
    create_database_engine,
)
from enterprise_knowledge_analytics_agent.persistence.models import (
    Chunk,
    Document,
    DocumentVersion,
)

pytestmark = pytest.mark.integration


@pytest.fixture
def database_engine() -> Iterator[Engine]:
    engine = create_database_engine()
    yield engine
    engine.dispose()


def test_unchanged_document_is_not_duplicated(
    tmp_path: Path,
    database_engine: Engine,
) -> None:
    source = tmp_path / "DOC-TEST.md"
    source.write_text(
        "# Test Policy\n\n## Paid Leave\n\nEligible employees receive 12 weeks.\n",
        encoding="utf-8",
    )
    source_uri = source.resolve().as_uri()

    try:
        first = ingest_markdown(source, database_engine)
        second = ingest_markdown(source, database_engine)

        with Session(database_engine) as session:
            document_count = session.scalar(
                select(func.count(Document.id)).where(Document.source_uri == source_uri)
            )
            version_count = session.scalar(
                select(func.count(DocumentVersion.id))
                .join(Document)
                .where(Document.source_uri == source_uri)
            )
            chunk_count = session.scalar(
                select(func.count(Chunk.id)).where(
                    Chunk.document_version_id == first.document_version_id
                )
            )

        assert first.status == "created"
        assert second.status == "unchanged"
        assert first.document_id == second.document_id
        assert first.document_version_id == second.document_version_id
        assert document_count == 1
        assert version_count == 1
        assert first.chunk_count > 0
        assert second.chunk_count == first.chunk_count
        assert chunk_count == first.chunk_count
    finally:
        with Session(database_engine) as session, session.begin():
            session.execute(delete(Document).where(Document.source_uri == source_uri))

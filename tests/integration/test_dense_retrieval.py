from pathlib import Path

import pytest

from enterprise_knowledge_analytics_agent.ingestion.service import ingest_markdown
from enterprise_knowledge_analytics_agent.persistence.database import (
    create_database_engine,
)
from enterprise_knowledge_analytics_agent.retrieval.dense import (
    embed_document_chunks,
    retrieve_dense,
)
from enterprise_knowledge_analytics_agent.retrieval.embeddings import (
    SentenceTransformerEmbeddingProvider,
)

pytestmark = pytest.mark.integration

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
DOC_001_PATH = REPOSITORY_ROOT / "data" / "documents" / "DOC-001-parental-leave-policy.md"


def test_dense_retrieval_finds_paid_parental_leave() -> None:
    engine = create_database_engine()
    provider = SentenceTransformerEmbeddingProvider()

    try:
        ingestion_result = ingest_markdown(DOC_001_PATH, engine)
        embedding_result = embed_document_chunks(
            external_id="DOC-001",
            provider=provider,
            engine=engine,
        )
        results = retrieve_dense(
            question="How many weeks of paid parental leave are available?",
            top_k=3,
            provider=provider,
            engine=engine,
        )
    finally:
        engine.dispose()

    assert ingestion_result.chunk_count == 7
    assert embedding_result.dimension == 384
    assert len(results) == 3
    assert any(
        result.section == "Paid Parental Leave" and "12 weeks" in result.content
        for result in results
    )

from pathlib import Path

import pytest

from enterprise_knowledge_analytics_agent.ingestion.service import ingest_markdown
from enterprise_knowledge_analytics_agent.persistence.database import (
    create_database_engine,
)
from enterprise_knowledge_analytics_agent.retrieval.dense import (
    embed_document_chunks,
)
from enterprise_knowledge_analytics_agent.retrieval.embeddings import (
    SentenceTransformerEmbeddingProvider,
)
from enterprise_knowledge_analytics_agent.retrieval.hybrid import retrieve_hybrid

pytestmark = pytest.mark.integration

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
DOC_004_PATH = REPOSITORY_ROOT / "data" / "documents" / "DOC-004-security-quick-reference.md"


def test_hybrid_retrieval_recovers_frozen_accidental_interaction_case() -> None:
    engine = create_database_engine()
    provider = SentenceTransformerEmbeddingProvider()

    try:
        ingest_markdown(DOC_004_PATH, engine)
        embed_document_chunks(
            external_id="DOC-004",
            provider=provider,
            engine=engine,
        )
        results = retrieve_hybrid(
            "What should I do after clicking a suspicious email link?",
            top_k=3,
            candidate_k=10,
            provider=provider,
            engine=engine,
        )
    finally:
        engine.dispose()

    assert len(results) == 3
    assert [result.rank for result in results] == [1, 2, 3]
    assert any(
        result.document_id == "DOC-004" and result.section == "Accidental Interaction"
        for result in results
    )

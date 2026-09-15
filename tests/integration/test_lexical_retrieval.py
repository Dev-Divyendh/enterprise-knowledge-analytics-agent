from pathlib import Path

import pytest

from enterprise_knowledge_analytics_agent.ingestion.service import ingest_markdown
from enterprise_knowledge_analytics_agent.persistence.database import (
    create_database_engine,
)
from enterprise_knowledge_analytics_agent.retrieval.lexical import retrieve_lexical

pytestmark = pytest.mark.integration

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
DOC_004_PATH = REPOSITORY_ROOT / "data" / "documents" / "DOC-004-security-quick-reference.md"


def test_lexical_retrieval_finds_accidental_interaction() -> None:
    engine = create_database_engine()

    try:
        ingest_markdown(DOC_004_PATH, engine)
        results = retrieve_lexical(
            "accidentally clicked suspicious link",
            top_k=3,
            engine=engine,
        )
    finally:
        engine.dispose()

    assert results
    assert results[0].document_id == "DOC-004"
    assert results[0].section == "Accidental Interaction"
    assert "clicked a suspicious link" in results[0].content
    assert results[0].similarity_score > 0


def test_lexical_retrieval_finds_frozen_accidental_interaction_case() -> None:
    engine = create_database_engine()

    try:
        ingest_markdown(DOC_004_PATH, engine)
        results = retrieve_lexical(
            "What should I do after clicking a suspicious email link?",
            top_k=3,
            engine=engine,
        )
    finally:
        engine.dispose()

    assert any(
        result.document_id == "DOC-004" and result.section == "Accidental Interaction"
        for result in results
    )

from pathlib import Path
from uuid import UUID

from enterprise_knowledge_analytics_agent.ingestion.markdown import (
    read_markdown_document,
)
from enterprise_knowledge_analytics_agent.processing.chunking import (
    MAX_CHUNK_TOKENS,
    build_chunks,
)


def test_chunker_preserves_sections(tmp_path: Path) -> None:
    source = tmp_path / "policy.md"
    source.write_text(
        "# Leave Policy\n\n"
        "Document ID: DOC-901\n\n"
        "## Eligibility\n\n"
        "Full-time employees are eligible.\n\n"
        "## Paid Leave\n\n"
        "Eligible employees receive 12 weeks of paid leave.\n",
        encoding="utf-8",
    )
    document = read_markdown_document(source)
    version_id = UUID("00000000-0000-0000-0000-000000000001")

    chunks = build_chunks(document, version_id)

    assert [chunk.ordinal for chunk in chunks] == [0, 1, 2]
    assert chunks[1].section_path == ["Leave Policy", "Eligibility"]
    assert chunks[2].section_path == ["Leave Policy", "Paid Leave"]
    assert chunks[2].content.startswith("Paid Leave")
    assert "12 weeks" in chunks[2].content


def test_chunk_ids_are_stable(tmp_path: Path) -> None:
    source = tmp_path / "policy.md"
    source.write_text(
        (
            "# Leave Policy\n\n"
            "Document ID: DOC-902\n\n"
            "## Paid Leave\n\n"
            "Employees receive 12 weeks.\n"
        ),
        encoding="utf-8",
    )
    document = read_markdown_document(source)
    version_id = UUID("00000000-0000-0000-0000-000000000001")

    first = build_chunks(document, version_id)
    second = build_chunks(document, version_id)

    assert [chunk.id for chunk in first] == [chunk.id for chunk in second]
    assert all(len(chunk.id) == 64 for chunk in first)


def test_oversized_section_is_split(tmp_path: Path) -> None:
    source = tmp_path / "long-policy.md"
    long_text = " ".join(f"term-{number}" for number in range(400))
    source.write_text(
        (f"# Leave Policy\n\nDocument ID: DOC-903\n\n## Long Section\n\n{long_text}\n"),
        encoding="utf-8",
    )
    document = read_markdown_document(source)
    version_id = UUID("00000000-0000-0000-0000-000000000001")

    chunks = build_chunks(document, version_id)

    assert len(chunks) > 1
    assert all(chunk.token_count <= MAX_CHUNK_TOKENS for chunk in chunks)

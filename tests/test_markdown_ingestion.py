from pathlib import Path

import pytest

from enterprise_knowledge_analytics_agent.ingestion.domain import ElementType
from enterprise_knowledge_analytics_agent.ingestion.markdown import (
    DocumentValidationError,
    calculate_sha256,
    read_markdown_document,
)


def test_sha256_is_stable() -> None:
    content = b"synthetic policy"

    assert calculate_sha256(content) == calculate_sha256(content)
    assert len(calculate_sha256(content)) == 64


def test_markdown_reader_preserves_sections(tmp_path: Path) -> None:
    source = tmp_path / "policy.md"
    source.write_text(
        "# Leave Policy\n\n## Paid Leave\n\nEligible employees receive 12 weeks of paid leave.\n",
        encoding="utf-8",
    )

    document = read_markdown_document(source)

    assert document.title == "Leave Policy"
    assert document.content_hash == calculate_sha256(source.read_bytes())
    assert [element.element_type for element in document.elements] == [
        ElementType.TITLE,
        ElementType.HEADING,
        ElementType.PARAGRAPH,
    ]
    assert document.elements[-1].section_path == [
        "Leave Policy",
        "Paid Leave",
    ]


def test_markdown_reader_rejects_wrong_type(tmp_path: Path) -> None:
    source = tmp_path / "policy.txt"
    source.write_text("Not allowed", encoding="utf-8")

    with pytest.raises(DocumentValidationError, match=r"only Markdown \(\.md\)"):
        read_markdown_document(source)


def test_markdown_reader_rejects_missing_file(tmp_path: Path) -> None:
    with pytest.raises(DocumentValidationError, match="does not exist"):
        read_markdown_document(tmp_path / "missing.md")

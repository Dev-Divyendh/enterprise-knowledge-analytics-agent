import pytest
from pydantic import ValidationError

from enterprise_knowledge_analytics_agent.ingestion.domain import (
    CanonicalDocument,
    CanonicalElement,
    CanonicalTable,
    ElementType,
)


def test_canonical_document_preserves_element_order() -> None:
    document = CanonicalDocument(
        source_uri="file:///policies/leave.md",
        title="Leave Policy",
        mime_type="text/markdown",
        content_hash="a" * 64,
        file_size_bytes=120,
        parser_name="docling",
        parser_version="2.121.0",
        elements=[
            CanonicalElement(
                id="element-1",
                element_type=ElementType.HEADING,
                text="Parental Leave",
            ),
            CanonicalElement(
                id="element-2",
                element_type=ElementType.PARAGRAPH,
                text="Eligible employees receive parental leave.",
            ),
        ],
    )

    assert [element.id for element in document.elements] == [
        "element-1",
        "element-2",
    ]


def test_table_element_requires_structured_table_data() -> None:
    with pytest.raises(ValidationError, match="structured table data"):
        CanonicalElement(
            id="table-1",
            element_type=ElementType.TABLE,
            text="Benefit table",
        )


def test_canonical_table_requires_equal_column_counts() -> None:
    with pytest.raises(ValidationError, match="same number of columns"):
        CanonicalTable(
            rows=[
                ["Benefit", "Employee cost"],
                ["Medical"],
            ],
            header_row_count=1,
        )


def test_non_table_element_rejects_table_data() -> None:
    with pytest.raises(ValidationError, match="only table elements"):
        CanonicalElement(
            id="paragraph-1",
            element_type=ElementType.PARAGRAPH,
            table=CanonicalTable(rows=[["unexpected"]]),
        )


def test_document_rejects_invalid_sha256_hash() -> None:
    with pytest.raises(ValidationError):
        CanonicalDocument(
            source_uri="file:///policies/leave.md",
            title="Leave Policy",
            mime_type="text/markdown",
            content_hash="not-a-sha256-hash",
            file_size_bytes=120,
            parser_name="docling",
            parser_version="2.121.0",
        )

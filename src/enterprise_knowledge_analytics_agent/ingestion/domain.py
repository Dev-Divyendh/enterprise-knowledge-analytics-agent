from enum import StrEnum
from typing import Any, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator


class StrictModel(BaseModel):
    """Base model that rejects unexpected input fields."""

    model_config = ConfigDict(extra="forbid")


class ElementType(StrEnum):
    """Supported structural elements in reading order."""

    TITLE = "title"
    HEADING = "heading"
    PARAGRAPH = "paragraph"
    LIST_ITEM = "list_item"
    TABLE = "table"
    IMAGE = "image"
    PAGE_BREAK = "page_break"


class CanonicalTable(StrictModel):
    """Rectangular table extracted from a source document."""

    rows: list[list[str]] = Field(min_length=1)
    header_row_count: int = Field(default=0, ge=0)

    @model_validator(mode="after")
    def validate_shape(self) -> Self:
        """Require at least one column and equal column counts."""

        column_count = len(self.rows[0])

        if column_count == 0:
            raise ValueError("table rows must contain at least one column")

        if any(len(row) != column_count for row in self.rows):
            raise ValueError("all table rows must have the same number of columns")

        if self.header_row_count > len(self.rows):
            raise ValueError("header_row_count cannot exceed the row count")

        return self


class CanonicalElement(StrictModel):
    """One ordered structural element extracted from a document."""

    id: str = Field(min_length=1)
    element_type: ElementType
    text: str = ""
    page_number: int | None = Field(default=None, ge=1)
    section_path: list[str] = Field(default_factory=list)
    table: CanonicalTable | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_table_data(self) -> Self:
        """Keep table structure attached only to table elements."""

        if self.element_type is ElementType.TABLE and self.table is None:
            raise ValueError("table elements require structured table data")

        if self.element_type is not ElementType.TABLE and self.table is not None:
            raise ValueError("only table elements may contain structured table data")

        return self


def empty_canonical_elements() -> list[CanonicalElement]:
    """Return a new typed element list for each document."""

    return []


class CanonicalDocument(StrictModel):
    """Parser-independent representation of one source document version."""

    source_uri: str = Field(min_length=1)
    title: str = Field(min_length=1)
    mime_type: str = Field(min_length=1)
    content_hash: str = Field(pattern=r"^[a-f0-9]{64}$")
    file_size_bytes: int = Field(ge=0)
    parser_name: str = Field(min_length=1)
    parser_version: str = Field(min_length=1)
    page_count: int | None = Field(default=None, ge=1)
    elements: list[CanonicalElement] = Field(default_factory=empty_canonical_elements)
    metadata: dict[str, Any] = Field(default_factory=dict)

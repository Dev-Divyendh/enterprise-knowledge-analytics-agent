import hashlib
import re
from pathlib import Path

from enterprise_knowledge_analytics_agent.ingestion.domain import (
    CanonicalDocument,
    CanonicalElement,
    ElementType,
)

MAX_MARKDOWN_FILE_BYTES = 1_048_576
HEADING_PATTERN = re.compile(r"^(#{1,6})\s+(.+?)\s*$")


class DocumentValidationError(ValueError):
    """Raised when a source document is unsafe or unsupported."""


def calculate_sha256(content: bytes) -> str:
    """Calculate a stable SHA-256 fingerprint for source bytes."""

    return hashlib.sha256(content).hexdigest()


def _element_id(content_hash: str, ordinal: int, text: str) -> str:
    identity = f"{content_hash}:{ordinal}:{text}".encode()
    return hashlib.sha256(identity).hexdigest()


def read_markdown_document(path: Path) -> CanonicalDocument:
    """Validate, read, hash, and parse one local Markdown document."""

    resolved_path = path.expanduser().resolve()

    if not resolved_path.exists():
        raise DocumentValidationError(f"document does not exist: {resolved_path}")

    if not resolved_path.is_file():
        raise DocumentValidationError(f"document is not a file: {resolved_path}")

    if resolved_path.suffix.lower() != ".md":
        raise DocumentValidationError("only Markdown (.md) files are currently allowed")

    file_size_bytes = resolved_path.stat().st_size

    if file_size_bytes == 0:
        raise DocumentValidationError("document must not be empty")

    if file_size_bytes > MAX_MARKDOWN_FILE_BYTES:
        raise DocumentValidationError(f"document exceeds the {MAX_MARKDOWN_FILE_BYTES}-byte limit")

    content = resolved_path.read_bytes()
    content_hash = calculate_sha256(content)

    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError as error:
        raise DocumentValidationError("Markdown document must use UTF-8") from error

    elements, title = _parse_markdown(text, content_hash)

    if not elements:
        raise DocumentValidationError("document contains no readable content")

    return CanonicalDocument(
        source_uri=resolved_path.as_uri(),
        title=title,
        mime_type="text/markdown",
        content_hash=content_hash,
        file_size_bytes=file_size_bytes,
        parser_name="markdown-baseline",
        parser_version="1.0",
        elements=elements,
        metadata={
            "external_id": "DOC-001",
            "source_filename": resolved_path.name,
        },
    )


def _parse_markdown(
    text: str,
    content_hash: str,
) -> tuple[list[CanonicalElement], str]:
    """Preserve Markdown headings and text blocks in reading order."""

    elements: list[CanonicalElement] = []
    section_levels: dict[int, str] = {}
    paragraph_lines: list[str] = []
    title: str | None = None

    def section_path() -> list[str]:
        return [section_levels[level] for level in sorted(section_levels)]

    def add_element(element_type: ElementType, element_text: str) -> None:
        normalized_text = " ".join(element_text.split())

        if not normalized_text:
            return

        ordinal = len(elements)
        elements.append(
            CanonicalElement(
                id=_element_id(content_hash, ordinal, normalized_text),
                element_type=element_type,
                text=normalized_text,
                section_path=section_path(),
            )
        )

    def flush_paragraph() -> None:
        if paragraph_lines:
            add_element(ElementType.PARAGRAPH, " ".join(paragraph_lines))
            paragraph_lines.clear()

    for raw_line in text.splitlines():
        stripped_line = raw_line.strip()
        heading_match = HEADING_PATTERN.match(stripped_line)

        if heading_match is not None:
            flush_paragraph()

            level = len(heading_match.group(1))
            heading_text = heading_match.group(2).strip()

            for existing_level in list(section_levels):
                if existing_level >= level:
                    del section_levels[existing_level]

            section_levels[level] = heading_text

            if level == 1 and title is None:
                title = heading_text
                add_element(ElementType.TITLE, heading_text)
            else:
                add_element(ElementType.HEADING, heading_text)

            continue

        if not stripped_line:
            flush_paragraph()
            continue

        if stripped_line.startswith(("- ", "* ")):
            flush_paragraph()
            add_element(ElementType.LIST_ITEM, stripped_line[2:])
            continue

        paragraph_lines.append(stripped_line)

    flush_paragraph()

    resolved_title = title or "Untitled document"
    return elements, resolved_title

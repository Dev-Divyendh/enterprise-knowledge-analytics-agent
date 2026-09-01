import hashlib
from dataclasses import dataclass
from uuid import UUID

from enterprise_knowledge_analytics_agent.ingestion.domain import (
    CanonicalDocument,
    CanonicalElement,
    ElementType,
)

MAX_CHUNK_TOKENS = 180
CHUNK_OVERLAP_TOKENS = 30
CHUNK_VERSION = 1


@dataclass(frozen=True)
class ChunkDraft:
    """Database-independent representation of a chunk to persist."""

    id: str
    ordinal: int
    chunk_version: int
    content: str
    content_hash: str
    token_count: int
    section_path: list[str]
    element_type: str
    metadata: dict[str, str]


def calculate_chunk_hash(content: str) -> str:
    """Calculate a stable fingerprint for normalized chunk content."""

    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def estimate_token_count(text: str) -> int:
    """Estimate tokens using whitespace-separated terms for the baseline."""

    return len(text.split())


def build_chunks(
    document: CanonicalDocument,
    document_version_id: UUID,
) -> list[ChunkDraft]:
    """Group canonical elements by section and enforce size boundaries."""

    section_groups = _group_elements_by_section(document)
    chunk_parts: list[tuple[str, list[str], str]] = []

    for section_name, section_path, section_text in section_groups:
        for part in _split_with_overlap(section_text):
            chunk_parts.append((section_name, section_path, part))

    chunks: list[ChunkDraft] = []

    for ordinal, (section_name, section_path, content) in enumerate(chunk_parts):
        content_hash = calculate_chunk_hash(content)
        chunk_id = _stable_chunk_id(
            document_version_id=document_version_id,
            ordinal=ordinal,
            content_hash=content_hash,
        )

        chunks.append(
            ChunkDraft(
                id=chunk_id,
                ordinal=ordinal,
                chunk_version=CHUNK_VERSION,
                content=content,
                content_hash=content_hash,
                token_count=estimate_token_count(content),
                section_path=list(section_path),
                element_type="section",
                metadata={
                    "document_title": document.title,
                    "section": section_name,
                    "source_uri": document.source_uri,
                    "token_count_method": "whitespace_estimate",
                },
            )
        )

    return chunks


def _group_elements_by_section(
    document: CanonicalDocument,
) -> list[tuple[str, list[str], str]]:
    """Combine headings with the text that belongs to each section."""

    groups: list[tuple[str, list[str], str]] = []
    section_name = document.title
    section_path = [document.title]
    section_elements: list[str] = []

    def flush_section() -> None:
        if not section_elements:
            return

        content = f"{section_name}\n\n" + "\n\n".join(section_elements)
        groups.append((section_name, list(section_path), content.strip()))
        section_elements.clear()

    for element in document.elements:
        if element.element_type is ElementType.TITLE:
            continue

        if element.element_type is ElementType.HEADING:
            flush_section()
            section_name = element.text
            section_path = list(element.section_path)
            continue

        if _contains_retrievable_text(element):
            section_elements.append(element.text)

    flush_section()
    return groups


def _contains_retrievable_text(element: CanonicalElement) -> bool:
    """Identify element types that currently contribute searchable text."""

    return element.element_type in {
        ElementType.PARAGRAPH,
        ElementType.LIST_ITEM,
    } and bool(element.text.strip())


def _split_with_overlap(text: str) -> list[str]:
    """Split oversized text using a fixed baseline token window."""

    tokens = text.split()

    if len(tokens) <= MAX_CHUNK_TOKENS:
        return [text]

    chunks: list[str] = []
    start = 0

    while start < len(tokens):
        end = min(start + MAX_CHUNK_TOKENS, len(tokens))
        chunks.append(" ".join(tokens[start:end]))

        if end == len(tokens):
            break

        start = end - CHUNK_OVERLAP_TOKENS

    return chunks


def _stable_chunk_id(
    document_version_id: UUID,
    ordinal: int,
    content_hash: str,
) -> str:
    """Create the same chunk ID for the same version, order, and content."""

    identity = f"{document_version_id}:{ordinal}:{CHUNK_VERSION}:{content_hash}"
    return hashlib.sha256(identity.encode("utf-8")).hexdigest()

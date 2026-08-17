# Enterprise Knowledge and Analytics Agent

An independent AI engineering portfolio project that combines grounded enterprise
document question answering with safe, read-only natural-language analytics.

> This repository uses a fictional organization, synthetic documents, and synthetic
> operational data. It does not represent work performed for an employer or client.

## Problem

Enterprise information is commonly divided between unstructured documents and
structured databases. Users need one interface for questions such as:

- How many days of parental leave are available?
- What receipts are required for hotel reimbursement?
- Can an employee work remotely from another state?
- How much did Engineering spend last quarter?
- Which departments had the highest travel expenses?

A general chatbot is insufficient because it may hallucinate policy details, ignore
document versions, follow malicious instructions embedded in documents, or generate
unsafe SQL.

This project builds a controlled system that routes each request to either:

1. A retrieval-augmented generation workflow for document questions.
2. A restricted Text-to-SQL workflow for approved analytics questions.
3. A clarification or refusal workflow when the request is ambiguous or unsafe.

## Portfolio milestone

The target is a portfolio-ready AI engineering system developed and verified in
approximately 90–120 focused hours.

Planned capabilities include:

- Multi-format parsing with Docling.
- OCR and table extraction.
- Content hashing, idempotency, lineage, and document versioning.
- Structure-aware chunking.
- Sentence Transformer embeddings.
- PostgreSQL and pgvector.
- Exact vector search and HNSW indexing.
- Lexical, dense, RRF hybrid, and cross-encoder-reranked retrieval.
- Grounded RAG with citations and abstention.
- Controlled LangGraph routing.
- AST-validated, read-only Text-to-SQL.
- Golden-dataset evaluation and MLflow tracking.
- FastAPI, Docker Compose, automated tests, and GitHub Actions.

These capabilities remain planned until their implementation and verification evidence
is recorded.

## Current verified status

The following foundation has been implemented and locally verified:

- Apple Silicon development environment.
- Python 3.12 compatibility baseline.
- `uv` project and dependency management.
- Locked dependencies through `uv.lock`.
- Installable `src/` package layout.
- Ruff linting and formatting.
- Pyright strict type checking.
- Pytest and coverage reporting.
- Pre-commit quality hooks.
- Initial package smoke test.

No AI, ingestion, retrieval, RAG, agent-routing, database, or Text-to-SQL capability is
currently claimed as implemented.

## Development setup

### Prerequisites

- Python 3.12
- `uv`
- Git
- Docker with Docker Compose

### Install the project

```bash
uv sync
```

### Run the current command-line smoke entry point

```bash
uv run enterprise-knowledge-analytics-agent
```

### Run quality checks

```bash
uv run ruff check .
uv run ruff format --check .
uv run pyright
uv run pytest --cov --cov-report=term-missing
uv run pre-commit run --all-files
```

## Evidence policy

Capabilities are tracked using four separate states:

1. Planned.
2. Implemented but not verified.
3. Implemented and verified.
4. Resume eligible.

A capability becomes resume eligible only after:

- The implementation exists.
- The project owner runs it.
- Relevant tests pass.
- Outputs or measurements are recorded.
- Reproduction instructions are documented.
- The design and trade-offs can be explained accurately.

Planned architecture will never be presented as completed work.

## Project status

Module 0 — Repository Foundation: **In progress**

See the project progress tracker and verified-achievements ledger under `docs/progress/`
once those files are introduced.

## License and data

A license will be selected before public release. All example business documents and
records will be original synthetic data or legally reusable public material with clear
attribution.

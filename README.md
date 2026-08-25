# Enterprise Knowledge and Analytics Agent

An independent AI engineering portfolio project that combines grounded enterprise document question answering with safe, read-only natural-language analytics.

> This repository uses a fictional organization, synthetic documents, and synthetic operational data. It does not represent work performed for an employer or client.

## Problem

Enterprise information is commonly divided between unstructured documents and structured databases. Users need one interface for questions such as:

* How many days of parental leave are available?
* What receipts are required for hotel reimbursement?
* Can an employee work remotely from another state?
* How much did Engineering spend last quarter?
* Which departments had the highest travel expenses?

A general chatbot is insufficient because it may hallucinate policy details, ignore document versions, follow malicious instructions embedded in documents, or generate unsafe SQL.

This project builds a controlled system that routes each request to:

1. A retrieval-augmented generation workflow for document questions.
2. A restricted Text-to-SQL workflow for approved analytics questions.
3. A clarification or refusal workflow when the request is ambiguous, unsupported, or unsafe.

## Portfolio milestone

The target is a portfolio-ready AI engineering system developed and verified in approximately 90–120 focused hours.

Target capabilities include:

* Multi-format parsing with Docling.
* OCR and table extraction.
* Content hashing, idempotency, lineage, and document versioning.
* Structure-aware chunking.
* Sentence Transformer embeddings.
* PostgreSQL and pgvector.
* Exact vector search and HNSW indexing.
* Lexical, dense, RRF hybrid, and cross-encoder-reranked retrieval.
* Grounded RAG with citations and abstention.
* Controlled LangGraph routing.
* AST-validated, read-only Text-to-SQL.
* Golden-dataset evaluation and MLflow tracking.
* FastAPI, Docker Compose, automated tests, and GitHub Actions.

Each capability remains planned until its implementation and verification evidence is recorded. Implemented capabilities are listed separately below.

## Current verified status

The following capabilities have been implemented and locally verified:

* Python 3.12, `uv`, locked dependencies, and an installable `src/` package.
* Ruff, Pyright strict mode, Pytest, coverage, and pre-commit checks.
* A versioned golden dataset containing 15 initial evaluation cases.
* PostgreSQL 17 and pgvector 0.8.6 through Docker Compose.
* SQLAlchemy models and Alembic migrations.
* Versioned document, chunk, embedding, processing, and evaluation storage.
* A separate synthetic analytics schema with four related tables.
* A database-enforced, least-privilege analytics reader role.
* Column-level protection for restricted employee data.
* Deterministic and idempotent synthetic analytics data.
* Seventeen passing automated tests, including eight PostgreSQL integration tests.

The current synthetic analytics dataset contains:

* 6 departments.
* 12 employees.
* 24 expense reports.
* 72 expense items.
* $28,500.00 in deterministic synthetic expenses.

Document ingestion, OCR, chunk generation, embedding generation, retrieval, RAG, Text-to-SQL generation and validation, LangGraph, FastAPI, MLflow, CI, and final service delivery remain planned.

## Development setup

### Prerequisites

* Python 3.12.
* `uv`.
* Git.
* Docker with Docker Compose.

### Install the project

```bash
uv sync --locked
```

### Create the local environment file

Create `.env` from the commit-safe example only if `.env` does not already exist:

```bash
if [ ! -f .env ]; then
  cp .env.example .env
fi
```

The real `.env` file is excluded from Git. Do not commit credentials or production secrets.

### Start PostgreSQL

```bash
docker compose up -d postgres
docker compose ps
```

The PostgreSQL service should report a healthy status.

### Apply database migrations

```bash
uv run alembic upgrade head
uv run alembic current
```

### Load the synthetic analytics dataset

```bash
uv run python -m \
  enterprise_knowledge_analytics_agent.persistence.seed_analytics
```

Expected counts:

```text
departments: 6
employees: 12
expense_reports: 24
expense_items: 72
```

The seed operation is deterministic and idempotent. Running it again should preserve the same row counts.

### Run the current command-line smoke entry point

```bash
uv run enterprise-knowledge-analytics-agent
```

### Run database integration tests

PostgreSQL must be running and migrations must be current.

```bash
uv run pytest tests/integration/test_database.py -v
```

### Run all quality checks

```bash
uv run ruff check .
uv run ruff format --check .
uv run pyright
uv run pytest --cov --cov-report=term-missing
uv run pre-commit run --all-files
```

### Stop local services

```bash
docker compose down
```

This stops the container without deleting the persistent PostgreSQL volume.

## Database organization

The local `enterprise_agent` PostgreSQL database currently uses two schemas:

### `public`

* `documents`
* `document_versions`
* `processing_runs`
* `chunks`
* `embeddings`
* `evaluation_runs`

### `analytics`

* `departments`
* `employees`
* `expense_reports`
* `expense_items`

The analytics reader role can query approved analytics data but cannot modify records or read restricted employee salary data.

## Evidence policy

Capabilities are tracked using four separate states:

1. Planned.
2. Implemented but not verified.
3. Implemented and verified.
4. Resume eligible.

A capability becomes resume eligible only after:

* The implementation exists.
* The project owner runs it.
* Relevant tests pass.
* Outputs or measurements are recorded.
* Reproduction instructions are documented.
* The design and trade-offs can be explained accurately.

Planned architecture will never be presented as completed work.

## Project status

* Module 0 — Repository foundation: **Implemented and verified**
* Module 1 — Business domain and golden dataset v0: **Implemented and verified**
* Module 2 — PostgreSQL and pgvector foundation: **Implemented and verified**
* Module 3 — Document ingestion: **Next**

See the progress tracker and verified-achievements ledger under `docs/progress/` for detailed evidence and limitations.

## License and data

A license will be selected before public release. All example business documents and records will be original synthetic data or legally reusable public material with clear attribution.

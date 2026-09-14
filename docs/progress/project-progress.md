# Project Progress Tracker

Last updated: 2026-09-14

## Status definitions

- **Planned:** Approved scope, but implementation has not started.
- **Implemented, not verified:** Code or configuration exists, but required execution,
  tests, measurements, documentation, or explanation are incomplete.
- **Implemented and verified:** The owner ran the capability, relevant checks passed,
  evidence was recorded, and reproduction instructions exist.
- **Resume eligible:** The capability is verified, materially relevant, reproducible,
  and can be explained accurately in an interview.

## Module status

| Module | Name | Status | Evidence |
|---|---|---|---|
| 0 | Repository foundation | Implemented and verified | 5 tests and initial Git commit |
| 1 | Business domain and golden dataset v0 | Implemented and verified | 15 cases and 4 validation tests |
| 2 | PostgreSQL and pgvector foundation | Implemented and verified | Migrations, permissions, seed data, and 8 integration tests |
| 3 | Document ingestion | Partially implemented and verified | DOC-001 Markdown ingestion, hashing, persistence, and idempotency |
| 4 | Processing and chunking | Partially implemented and verified | 7 structure-aware DOC-001 chunks and 3 unit tests |
| 5 | Embeddings and vector indexing | Partially implemented and verified | 7 normalized BGE embeddings stored in pgvector |
| 6 | Retrieval experiments | Partially implemented and verified | Exact dense retrieval baseline and integration test |
| 7 | Grounded RAG | Partially implemented and verified | Real Ollama answer, citation, abstention, and 2 integration tests |
| 8 | Safe Text-to-SQL | Planned | Database and reader-role foundation only |
| 9 | Controlled LangGraph workflow | Planned | None |
| 10 | FastAPI and containerized service | Partially implemented and verified | Health, readiness, and RAG question endpoints |
| 11 | Golden evaluation and MLflow | Partially implemented | Golden v0.1 exists; measured evaluation runner not implemented |
| 12 | Focused observability | Partially implemented | Scores, model/prompt versions, tokens, and selected latency values |
| 13 | Focused testing and security | Partially implemented and verified | 35 tests; citation, abstention, database permission tests |
| 14 | CI and portfolio packaging | Planned | Existing documentation only; CI not implemented |

## Module 0 checklist

- [x] Create a new Git repository on the `main` branch.
- [x] Install and verify Python 3.12.
- [x] Install and verify `uv`.
- [x] Create `pyproject.toml` and the `src/` package layout.
- [x] Create a locked virtual environment.
- [x] Configure Ruff.
- [x] Configure Pyright strict mode.
- [x] Configure Pytest and coverage.
- [x] Add and verify the initial smoke test.
- [x] Add repository-level ignore rules.
- [x] Install and verify pre-commit hooks.
- [x] Create the initial README.
- [x] Create an ADR template.
- [x] Create and test the application configuration foundation.
- [x] Complete the Module 0 knowledge check.
- [x] Run the final Module 0 quality gate.
- [x] Create the initial Git commit.

## Module 1 checklist

- [x] Define the fictional organization and system boundaries.
- [x] Define the initial document corpus.
- [x] Define approved and prohibited analytics.
- [x] Define policy, analytics, clarification, and refusal routes.
- [x] Create golden dataset v0.1 with 15 cases.
- [x] Validate JSON syntax and unique case IDs.
- [x] Implement a typed Pydantic golden-dataset loader.
- [x] Enforce route-specific dataset requirements.
- [x] Add and pass four dataset-validation tests.
- [x] Record actual route distribution and test results.

## Module 2 checklist

- [x] Run PostgreSQL through Docker Compose.
- [x] Install and verify pgvector 0.8.6.
- [x] Configure SQLAlchemy, Psycopg, and connection pooling.
- [x] Configure Alembic migrations.
- [x] Create document, version, processing, chunk, embedding, and evaluation tables.
- [x] Create the separate `analytics` schema.
- [x] Create department, employee, expense-report, and expense-item tables.
- [x] Verify migration upgrade, downgrade, and re-upgrade behavior.
- [x] Verify PostgreSQL full-text and pgvector column types.
- [x] Create and test a least-privilege analytics reader role.
- [x] Block salary access and database writes.
- [x] Create deterministic, idempotent synthetic analytics data.
- [x] Add and pass eight PostgreSQL integration tests.
- [x] Record the PostgreSQL and pgvector architecture decision.
- [x] Create the cumulative interview-question bank.
- [x] Create and push the Module 2 Git commit.

## First RAG vertical-slice checklist

- [x] Read and validate synthetic Markdown policy DOC-001.
- [x] Calculate and persist its SHA-256 content hash.
- [x] Persist one document and one active document version.
- [x] Verify unchanged-document idempotency.
- [x] Create and persist seven structure-aware chunks.
- [x] Generate normalized 384-dimensional embeddings using
  `BAAI/bge-small-en-v1.5`.
- [x] Store seven embeddings in PostgreSQL/pgvector.
- [x] Verify embedding idempotency.
- [x] Perform exact dense retrieval.
- [x] Retrieve the Paid Parental Leave section at rank one for the supported
  question.
- [x] Generate a grounded answer using local `qwen3.5:4b` through Ollama.
- [x] Return an application-controlled DOC-001 citation.
- [x] Abstain from unsupported questions when evidence is insufficient.
- [x] Verify that abstention avoids calling the LLM.
- [x] Expose the workflow through `POST /api/v1/questions`.
- [x] Manually verify supported and unsupported HTTP requests.
- [x] Pass deterministic RAG and FastAPI integration tests.
- [x] Pass the complete 35-test quality gate.

The first RAG vertical slice is implemented and verified. Broader retrieval evaluation,
lexical and hybrid retrieval, Text-to-SQL, LangGraph, and final portfolio packaging
remain incomplete.

## Deferred project-wide knowledge review

- [ ] Review the cumulative interview-question bank after implementation is complete.
- [ ] Complete the final project knowledge exam before creating resume bullets.

## Current blockers

None.

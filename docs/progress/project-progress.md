# Project Progress Tracker

Last updated: 2026-09-15

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
| 3 | Document ingestion | Partially implemented and verified | Six Markdown documents with extracted identities, hashing, persistence, and idempotency |
| 4 | Processing and chunking | Partially implemented and verified | 35 structure-aware chunks across six documents |
| 5 | Embeddings and vector indexing | Partially implemented and verified | 35 normalized BGE embeddings stored in pgvector |
| 6 | Retrieval experiments | Partially implemented and verified | Frozen v0.2 comparison of exact dense, PostgreSQL full-text, and RRF hybrid Top-3 retrieval |
| 7 | Grounded RAG | Partially implemented and verified | 18-case deterministic evaluation plus real Ollama prompt-injection demonstration |
| 8 | Safe Text-to-SQL | Planned | Database and reader-role foundation only |
| 9 | Controlled LangGraph workflow | Planned | None |
| 10 | FastAPI and containerized service | Partially implemented and verified | Health, readiness, and RAG question endpoints |
| 11 | Golden evaluation and MLflow | Partially implemented and verified | Frozen 18-case retrieval dataset and reproducible JSON reports; MLflow deferred |
| 12 | Focused observability | Partially implemented | Scores, model/prompt versions, tokens, and selected latency values |
| 13 | Focused testing and security | Partially implemented and verified | 48 passing tests; lexical and hybrid real-PostgreSQL regressions plus existing RAG safety tests |
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

## Interview-ready Milestone 1 checklist

- [x] Create a six-document synthetic Markdown corpus.
- [x] Extract and validate unique `DOC-\d{3}` identifiers.
- [x] Ingest all six documents idempotently.
- [x] Persist 35 structure-aware chunks with source lineage.
- [x] Persist 35 normalized BGE-small embeddings.
- [x] Create and freeze golden dataset v0.2 with 18 policy cases.
- [x] Include 14 answerable and four unsupported cases.
- [x] Include conflict and malicious-document cases.
- [x] Implement transparent retrieval metrics.
- [x] Measure exact-dense Top-3 and Top-5 retrieval.
- [x] Measure deterministic RAG behavior, citations, and abstention.
- [x] Verify that all unsupported cases avoid the LLM.
- [x] Verify one malicious-document case using deterministic controls.
- [x] Manually verify the malicious case with real local `qwen3.5:4b`.
- [x] Preserve known dense-retrieval failures for hybrid comparison.
- [x] Pass the complete 42-test quality gate with 81% coverage.

Milestone 1 is implemented and verified. The next milestone is PostgreSQL lexical
retrieval, RRF fusion, and comparison against these frozen dense baselines.
## Interview-ready Milestone 2 — retrieval comparison

- [x] Reuse the generated chunk `tsvector` column and GIN index.
- [x] Implement and test PostgreSQL lexical retrieval on active document versions.
- [x] Preserve the first AND-style lexical baseline: Hit Rate@3 0.2143.
- [x] Evaluate OR-term lexical retrieval: Hit Rate@3 1.0000, Recall@3 1.0000, MRR 0.7619.
- [x] Implement deterministic chunk-ID RRF fusion using 10 candidates per retriever.
- [x] Evaluate hybrid Top-3: Hit Rate 1.0000, Recall 0.9643, MRR 0.8452.
- [x] Verify the real hybrid path recovers KNO-014 within Top-3.
- [x] Pass 48 tests with 81% coverage.

Hybrid improved Top-3 evidence coverage relative to dense, but did not improve
overall MRR. KNO-006 remains incomplete, and malicious DOC-007 content ranks first
for KNO-008 and KNO-014 in some retrieval modes. The existing RAG answer endpoint
still uses dense retrieval and its cosine-based abstention threshold.

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

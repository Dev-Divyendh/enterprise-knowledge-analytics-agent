# Project Progress Tracker

Last updated: 2026-09-18

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
| 0 | Repository foundation | Implemented and verified | Python 3.12 package, locked environment, configuration, quality tools, and initial commit |
| 1 | Business domain and golden dataset v0 | Implemented and verified | 15 initial cases and four validation tests |
| 2 | PostgreSQL and pgvector foundation | Implemented and verified | Migrations, permissions, seed data, and eight integration tests |
| 3 | Document ingestion | Partially implemented and verified | Six Markdown documents with identity extraction, hashing, persistence, versioning, and idempotency |
| 4 | Processing and chunking | Partially implemented and verified | 35 structure-aware chunks across six documents |
| 5 | Embeddings and vector indexing | Partially implemented and verified | 35 normalized BGE-small embeddings stored in pgvector |
| 6 | Retrieval experiments | Partially implemented and verified | Frozen v0.2 comparison of exact dense, PostgreSQL lexical, and RRF hybrid retrieval |
| 7 | Grounded RAG | Partially implemented and verified | Citations, abstention, deterministic evaluation, and real Ollama safety demonstration |
| 8 | Safe Text-to-SQL | Implemented and verified | SQLGlot validation, semantic contracts, read-only execution, and real Qwen verification |
| 9 | Controlled LangGraph workflow | Implemented and verified | Deterministic four-route graph for RAG, Text-to-SQL, clarification, and refusal |
| 10 | FastAPI and containerized service | Partially implemented and verified | Unified workflow API; PostgreSQL containerized, application containerization deferred |
| 11 | Golden evaluation and MLflow | Partially implemented and verified | Frozen 18-case RAG dataset and reproducible reports; MLflow deferred |
| 12 | Focused observability | Implemented and verified | Structured JSON logs, request IDs, route, outcome, model, token, score, and latency fields |
| 13 | Focused testing and security | Partially implemented and verified | 96 tests, 82% coverage, RAG and SQL safeguards; authentication and load testing deferred |
| 14 | CI and portfolio packaging | Implemented and verified | Green GitHub Actions workflow, final README, architecture guide, security review, and reproducible evidence |

## Module 0 — repository foundation

- [x] Create a Git repository on the `main` branch.
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
- [x] Create and test typed application settings.
- [x] Run the Module 0 quality gate.
- [x] Create and push the initial Git commit.

## Module 1 — domain and golden dataset

- [x] Define the fictional enterprise policy domain.
- [x] Define the synthetic expense-analytics domain.
- [x] Create golden dataset v0.1.
- [x] Include policy-RAG, Text-to-SQL, clarification, and refusal cases.
- [x] Validate route-specific requirements.
- [x] Reject duplicate case identifiers.
- [x] Pass four golden-dataset tests.

## Module 2 — PostgreSQL and pgvector foundation

- [x] Run PostgreSQL through Docker Compose.
- [x] Install and verify pgvector 0.8.6.
- [x] Configure SQLAlchemy, Psycopg, and connection pooling.
- [x] Configure Alembic migrations.
- [x] Create document, version, processing, chunk, embedding, and evaluation tables.
- [x] Create the separate `analytics` schema.
- [x] Create department, employee, expense-report, and expense-item tables.
- [x] Verify migration upgrade, downgrade, and re-upgrade behavior.
- [x] Verify PostgreSQL `tsvector` and pgvector `vector` storage.
- [x] Create and test a least-privilege analytics reader role.
- [x] Block salary access and database writes.
- [x] Create deterministic, idempotent synthetic analytics data.
- [x] Add and pass eight PostgreSQL integration tests.
- [x] Record the PostgreSQL and pgvector architecture decision.
- [x] Create the cumulative interview-question bank.
- [x] Create and push the Module 2 commit.

## Milestone 1 — small-corpus RAG evaluation

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
- [x] Verify all unsupported cases avoid the LLM.
- [x] Verify the malicious case using deterministic controls.
- [x] Manually verify the malicious case with local `qwen3.5:4b`.
- [x] Preserve known dense-retrieval failures for comparison.
- [x] Pass the 42-test quality gate with 81% coverage.

### Milestone 1 result

Exact dense retrieval produced:

- Top-3 Hit Rate: `0.9286`.
- Top-3 Recall: `0.8929`.
- Top-3 MRR: `0.8929`.
- Top-5 Hit Rate: `1.0000`.
- Top-5 Recall: `0.9643`.
- Top-5 MRR: `0.9107`.

The deterministic RAG evaluation produced:

- Supported-answer rate: `1.0000`.
- Unsupported abstention rate: `1.0000`.
- Citation hit rate: `0.9286`.
- Complete citation recall: `0.8571`.

KNO-006 retained incomplete conflict evidence, and KNO-014 missed its expected
section at dense Top-3.

## Milestone 2 — retrieval comparison

- [x] Reuse the generated chunk `tsvector` column and GIN index.
- [x] Implement PostgreSQL lexical retrieval on active document versions.
- [x] Preserve the initial AND-style lexical baseline.
- [x] Evaluate OR-term lexical retrieval.
- [x] Implement deterministic chunk-ID RRF fusion.
- [x] Retrieve up to ten candidates from each component retriever.
- [x] Avoid comparing incompatible lexical and cosine raw scores.
- [x] Evaluate hybrid Top-3 retrieval.
- [x] Verify the real hybrid path recovers KNO-014 within Top-3.
- [x] Pass 48 tests with 81% coverage.

### Milestone 2 result

| Retrieval system | Hit Rate@3 | Recall@3 | Precision@3 | MRR@3 |
|---|---:|---:|---:|---:|
| Exact dense | 0.9286 | 0.8929 | 0.3333 | 0.8929 |
| PostgreSQL lexical OR | 1.0000 | 1.0000 | 0.4286 | 0.7619 |
| RRF hybrid | 1.0000 | 0.9643 | 0.3571 | 0.8452 |

Hybrid improved Top-3 evidence coverage relative to dense retrieval but did not
improve overall MRR. KNO-006 remains incomplete, and malicious DOC-007 content can
rank first for selected cases.

The API answer path remains dense-only because the existing cosine threshold cannot
be applied directly to RRF scores.

## Milestone 3 — safe Text-to-SQL

- [x] Install and lock SQLGlot 30.18.0.
- [x] Implement single-statement PostgreSQL `SELECT` validation.
- [x] Restrict queries to allowlisted analytics tables and columns.
- [x] Reject destructive SQL and multiple statements.
- [x] Reject CTEs, subqueries, wildcards, locking queries, and `SELECT INTO`.
- [x] Reject restricted columns and non-analytics schemas.
- [x] Reject unknown functions and excessive limits.
- [x] Add mandatory `LIMIT 100` when no limit is supplied.
- [x] Execute validated SQL inside a read-only transaction.
- [x] Assume the least-privilege `enterprise_agent_analytics_reader` role.
- [x] Apply a three-second PostgreSQL statement timeout.
- [x] Generate structured SQL through the existing LLM-provider interface.
- [x] Require operation-specific tables, filters, aggregates, aliases, dates, and grouping.
- [x] Validate database-result shape and values.
- [x] Preserve an incorrect real-model query as a regression test.
- [x] Verify the corrected path with local `qwen3.5:4b`.
- [x] Return deterministic clarification for incomplete analytics questions.
- [x] Refuse destructive and restricted-data requests without calling the LLM.
- [x] Pass the 65-test quality gate with 81% coverage.

### Milestone 3 result

The verified operation answers:

> How much did Engineering spend on paid expense reports in 2025?

The result was four reports totaling `$3,250.00`.

This remains one explicitly allowlisted analytics operation, not a general-purpose
natural-language database interface.

## Milestone 4 — controlled LangGraph workflow

- [x] Install and lock LangGraph 1.2.11.
- [x] Define a unified workflow response model.
- [x] Implement deterministic policy, analytics, clarification, and refusal routing.
- [x] Route only the approved analytics operation to Text-to-SQL.
- [x] Route incomplete analytics requests to clarification.
- [x] Route destructive and restricted-data requests to refusal.
- [x] Route policy questions to grounded RAG.
- [x] Build and compile a typed LangGraph `StateGraph`.
- [x] Add explicit start, router, execution, and end transitions.
- [x] Verify clarification and refusal without model or database execution.
- [x] Verify the RAG graph branch using real retrieval and a deterministic LLM.
- [x] Verify the SQL branch using real PostgreSQL and a deterministic LLM.
- [x] Replace the RAG-only API endpoint with the unified workflow endpoint.
- [x] Test all four routes across the FastAPI boundary.
- [x] Manually verify all routes using real local providers.
- [x] Pass the 90-test quality gate with 82% coverage.

### Milestone 4 result

The graph routes requests to:

- `policy_rag`
- `text_to_sql`
- `clarification`
- `refusal`

Routing is deterministic and application-controlled. LangGraph coordinates the
services but does not replace the security boundaries enforced by RAG thresholds,
SQLGlot, application allowlists, result validation, or PostgreSQL permissions.

## Milestone 5 — observability, CI, and portfolio packaging

### Structured observability

- [x] Add a dedicated observability package.
- [x] Emit machine-readable JSON logs.
- [x] Create or preserve safe request IDs.
- [x] Reject unsafe caller-supplied request IDs.
- [x] Return `X-Request-ID` on API responses.
- [x] Preserve request context only for the lifetime of the request.
- [x] Log request method, path, status, and latency.
- [x] Log workflow route and outcome.
- [x] Log abstention, model identity, token counts, and retrieval score.
- [x] Avoid logging questions, SQL, result rows, retrieved text, or credentials.
- [x] Add five deterministic observability tests.
- [x] Verify request-ID propagation across the FastAPI boundary.

### Continuous integration

- [x] Create `.github/workflows/ci.yml`.
- [x] Run CI on pushes to `main`.
- [x] Run CI on pull requests.
- [x] Restrict workflow permissions to read-only repository contents.
- [x] Pin GitHub Actions by commit SHA.
- [x] Install Python 3.12 and locked dependencies.
- [x] Run Ruff lint and formatting checks.
- [x] Run Pyright strict checks.
- [x] Run deterministic tests with coverage.
- [x] Exclude PostgreSQL integration tests from the service-free CI job.
- [x] Supply a non-connecting placeholder database URL for engine construction.
- [x] Reproduce the CI environment locally.
- [x] Verify a successful GitHub-hosted workflow run.
- [x] Preserve the initial CI configuration failure as troubleshooting evidence.

### Portfolio documentation

- [x] Replace the outdated README with the verified system status.
- [x] Add detailed architecture documentation.
- [x] Add a consolidated security and limitations review.
- [x] Update the verified-achievements ledger.
- [x] Validate all documentation links and referenced command paths.
- [x] Run the final complete quality gate.
- [x] Commit and push the final documentation.
- [ ] Complete the project concept walkthrough.
- [ ] Complete the interview knowledge review.
- [ ] Prepare final resume bullets only after the knowledge review.

## Current verification baseline

### Complete local suite

```text
96 passed
82% statement coverage
0 Ruff failures
0 Pyright errors
0 Pyright warnings
All configured pre-commit hooks passed
```

The full suite includes 26 integration tests using the real local PostgreSQL service.

### Deterministic CI suite

```text
70 passed
26 integration tests deselected
67% statement coverage for the deterministic subset
```

The deterministic suite does not require PostgreSQL or Ollama.

### GitHub Actions

The workflow for commit `93bacd1` completed successfully on a GitHub-hosted Ubuntu
runner. The preceding run correctly exposed a missing CI environment setting, which
was reproduced locally and fixed with a non-connecting placeholder database URL.

## Deferred scope

The following items are optional or intentionally deferred:

- PDF and Office-document parsing.
- OCR and table extraction.
- Cross-encoder reranking.
- MLflow.
- Authentication and API authorization.
- Rate limiting.
- Load testing.
- FastAPI application containerization.
- Cloud deployment.
- Kubernetes.
- Persistent LangGraph checkpoints.
- Conversation memory.
- External tracing.

These items must not be represented as implemented.

## Deferred knowledge review

- [ ] Review the full architecture and request lifecycle.
- [ ] Explain the ingestion and retrieval pipelines without notes.
- [ ] Explain retrieval metrics and measured trade-offs.
- [ ] Explain grounding, citations, abstention, and prompt-injection controls.
- [ ] Explain Text-to-SQL validation layers.
- [ ] Explain deterministic routing versus autonomous agents.
- [ ] Explain structured logging and request correlation.
- [ ] Explain local integration testing versus service-free CI.
- [ ] Complete the cumulative interview-question bank.
- [ ] Complete the final project knowledge exam.
- [ ] Create resume bullets after the knowledge review.

## Current blockers

## Current blockers

None.

The scoped portfolio implementation is complete and verified. The remaining work is
the separate learning and interview-preparation phase:

1. Review the complete architecture and pipelines.
2. Complete the cumulative interview-question bank.
3. Complete the final project knowledge exam.
4. Prepare evidence-bounded resume bullets.
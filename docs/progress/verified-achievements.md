# Verified Achievements Ledger

Last updated: 2026-09-15

This ledger records only capabilities supported by execution evidence. It does not
convert planned architecture into completed work.

## Implemented and verified

### Repository and Python foundation

- Created a new Git repository on the `main` branch at
  `enterprise-knowledge-analytics-agent`.
- Installed and executed CPython 3.12.14 on macOS ARM64.
- Initialized an installable Python package using a `src/` layout.
- Created a project-local virtual environment using `uv`.
- Generated and retained a reproducible `uv.lock` dependency lockfile.
- Built and installed package version `0.1.0` in the local environment.
- Executed the generated project command successfully.

### Automated quality foundation

- Executed Ruff 0.16.3 with all current lint checks passing.
- Verified Ruff formatting for all current Python files.
- Executed Pyright 1.1.411 in strict mode with zero errors and zero warnings.
- Executed Pytest 9.1.1 with one of one tests passing.
- Recorded 100% coverage of the current two-statement scaffold.
- Installed a repository pre-commit hook.
- Executed Ruff and Pyright successfully through pre-commit.

### Application configuration foundation

- Installed and locked Pydantic 2.13.4 and Pydantic Settings 2.15.0.
- Implemented environment-prefixed, typed application settings.
- Added safe defaults and validation boundaries for request configuration.
- Added a commit-safe `.env.example` while excluding real `.env` files.
- Verified default loading, environment-variable parsing, Boolean and integer
  conversion, and invalid-timeout rejection with three automated tests.
- Executed strict Pyright checking with zero diagnostics after correcting test
  isolation.

  ### Business domain and golden dataset v0

- Defined a synthetic enterprise policy and expense-analytics domain.
- Created golden dataset v0.1 containing 15 routing, grounding, clarification, and
  refusal cases.
- Recorded 8 policy-RAG, 3 Text-to-SQL, 2 clarification, and 2 refusal expectations.
- Implemented strict Pydantic models with route-specific validation and duplicate-ID
  rejection.
- Passed four golden-dataset validation tests.

### PostgreSQL and pgvector foundation

- Ran PostgreSQL 17.11 and pgvector 0.8.6 locally through Docker Compose.
- Implemented SQLAlchemy engine creation with connection pooling and stale-connection
  checks.
- Configured Alembic and verified four ordered migrations.
- Created and verified six application tables in the `public` schema.
- Created and verified four business tables in the `analytics` schema.
- Verified PostgreSQL `tsvector` and pgvector `vector` storage types.
- Verified migration downgrade and re-upgrade behavior before loading data.
- Added database constraints, foreign keys, unique rules, and retrieval indexes.

### Analytics data and database security

- Created deterministic synthetic data containing 6 departments, 12 employees,
  24 expense reports, and 72 expense items.
- Verified that rerunning the seed operation preserved the same row counts.
- Created a non-login, least-privilege analytics reader role.
- Verified approved reads across all four analytics tables.
- Verified that the reader cannot access `annual_salary`.
- Verified that the reader cannot modify analytics records.
- Verified database rejection of nonpositive expense amounts.
- Measured total synthetic expenses of `$28,500.00`.
- Recorded department totals ranging from `$3,250.00` for Engineering to `$6,250.00`
  for Operations.

### Module 2 automated verification

- Passed eight PostgreSQL integration tests.
- Passed all 17 current project tests in 0.76 seconds.
- Recorded 95% statement coverage for the currently implemented code.
- Passed Ruff formatting and linting.
- Passed Pyright strict checking with zero diagnostics.

### First grounded RAG vertical slice

- Ingested synthetic Markdown policy DOC-001 and calculated SHA-256 hash
  `315276f385ea810f045b170ac3c96e39e1428b5227a1b705dfa2b5ed397865be`.
- Persisted DOC-001 as one document and one active document version containing
  18 canonical elements.
- Verified unchanged-document idempotency by rerunning ingestion without creating
  a duplicate version.
- Created and persisted seven structure-aware chunks preserving section and
  document-version lineage.
- Generated and stored seven normalized 384-dimensional embeddings using
  `BAAI/bge-small-en-v1.5` version `v1.5`.
- Verified embedding idempotency: the initial operation created seven embeddings
  and the repeated operation created zero.
- Implemented exact dense retrieval through PostgreSQL/pgvector.
- Retrieved the Paid Parental Leave section at rank one with similarity `0.87207`
  for the demonstrated supported question.
- Integrated local `qwen3.5:4b` through a provider-independent LLM interface and
  Ollama 0.33.3.
- Generated the grounded answer “Up to 12 weeks of paid parental leave are
  available.”
- Returned an application-controlled citation to DOC-001, Parental Leave Policy,
  section Paid Parental Leave.
- Implemented evidence-based abstention using a provisional `0.70` retrieval
  threshold.
- Manually verified unsupported-question abstention with no citation, no LLM model,
  and no recorded token use.
- Exposed health, database-readiness, and grounded question-answering endpoints
  through FastAPI.
- Manually verified the supported and unsupported workflows through
  `POST /api/v1/questions`.
- Passed deterministic integration tests proving supported citation behavior and
  that unsupported-question abstention does not call the LLM.
- Passed all 35 current tests with 86% statement coverage.
- Passed Ruff linting and formatting, Pyright strict checking, and all configured
  pre-commit hooks.

The `0.70` abstention threshold is provisional and must be calibrated using the
expanded golden evaluation dataset. The successful examples do not establish
general retrieval accuracy, production reliability, or scalability.

### Small-corpus and RAG evaluation milestone

- Created and ingested six synthetic Markdown policy documents with distinct validated
  document identifiers.
- Persisted 35 structure-aware chunks and 35 normalized 384-dimensional
  `BAAI/bge-small-en-v1.5` embeddings.
- Verified unchanged-document ingestion across all six documents.
- Created frozen golden dataset v0.2 containing 18 policy-RAG cases: 14 answerable
  and four unsupported.
- Implemented transparent Hit Rate@K, Recall@K, Precision@K, MRR, citation, abstention,
  LLM-call, and latency measurements.
- Measured exact dense Top-3 retrieval: Hit Rate 0.9286, Recall 0.8929,
  Precision 0.3333, and MRR 0.8929.
- Measured exact dense Top-5 retrieval: Hit Rate 1.0000, Recall 0.9643,
  Precision 0.2143, and MRR 0.9107.
- Measured deterministic Top-3 RAG behavior: 100% supported-answer rate, 100%
  unsupported abstention rate, 0.9286 citation hit rate, and 0.8571 complete citation
  recall.
- Verified that all four unsupported cases abstained without calling the LLM.
- Verified that the malicious DOC-007 fixture was supplied as untrusted evidence under
  explicit application safety instructions.
- Manually demonstrated that local `qwen3.5:4b` answered the malicious-document case
  using safe DOC-004 evidence without following the embedded instruction.
- Preserved two known limitations: KNO-006 retrieved only part of the required conflict
  evidence, and KNO-014 missed its expected section at Top-3.
- Generated reproducible dense Top-3, dense Top-5, and deterministic RAG JSON reports.
- Passed all 42 tests with 81% statement coverage.

## Implemented but not fully verified

- Module 0 knowledge validation is deferred pending review of the project owner's
  written notebook answers.
  - Module 2 implementation is verified, but the owner’s interview knowledge check has
  not yet been completed.

## Planned

PostgreSQL lexical retrieval, RRF hybrid comparison, safe Text-to-SQL, controlled
LangGraph routing, structured logging, CI, and final portfolio packaging remain.

PDF parsing, OCR, reranking, MLflow, authentication, load testing, cloud deployment,
and complete application containerization remain optional or deferred.

## Planned

Multi-document evaluation, PostgreSQL lexical retrieval, RRF hybrid retrieval,
threshold calibration, malicious-document testing, SQL generation and `sqlglot`
validation, controlled LangGraph routing, structured application logging, CI, and
final portfolio packaging remain planned.

Docling PDF parsing, OCR, table extraction, reranking, MLflow, authentication, load
testing, and complete application containerization are optional under the revised
interview-ready scope.

## Resume eligible

- Built and evaluated a local enterprise RAG pipeline using structure-aware Markdown
  ingestion, BGE-small embeddings, PostgreSQL/pgvector exact retrieval, grounded local
  LLM generation, application-controlled citations, and evidence-based abstention.
- Created a frozen 18-case evaluation dataset and measured Top-3/Top-5 retrieval,
  citation correctness, abstention behavior, and one malicious-document scenario.

These claims describe the current RAG subsystem only. Hybrid retrieval, Text-to-SQL,
LangGraph orchestration, production scale, and deployment are not yet resume-eligible.

## Recorded measurements

| Date | Measurement | Result | Context |
|---|---|---:|---|
| 2026-08-17 | Smoke tests passed | 1/1 | Generated package scaffold |
| 2026-08-17 | Scaffold statement coverage | 100% | Two executable statements only |
| 2026-08-17 | Smoke-test runtime | 0.02 seconds | Local Apple Silicon environment |
| 2026-08-17 | Pyright diagnostics | 0 | Strict mode |
| 2026-08-17 | Pre-commit checks passed | 3/3 | Ruff lint, Ruff format, Pyright |
| 2026-08-17 | Configuration tests passed | 3/3 | Defaults, environment parsing, invalid input |
| 2026-08-17 | Final Module 0 tests passed | 5/5 | Smoke and configuration tests |
| 2026-08-17 | Module 0 statement coverage | 100% | 17 foundation statements |
| 2026-08-17 | Final Module 0 test runtime | 0.11 seconds | Local Apple Silicon environment |
| 2026-08-19 | Golden dataset cases | 15 | Version 0.1.0, specification-only |
| 2026-08-19 | Golden dataset tests | 4/4 | Loader, routes, duplicates, SQL requirements |
| 2026-08-19 | Total project tests | 9/9 | Module 0 and Module 1 |
| 2026-08-19 | Project statement coverage | 93% | 74 statements, branch coverage enabled |
| 2026-08-19 | Test-suite runtime | 0.12 seconds | Local Apple Silicon environment |
| 2026-08-25 | PostgreSQL version | 17.11 | Docker Compose on macOS ARM64 |
| 2026-08-25 | pgvector version | 0.8.6 | PostgreSQL extension |
| 2026-08-25 | Application tables | 10 | 6 public and 4 analytics tables |
| 2026-08-25 | Integration tests passed | 8/8 | Real local PostgreSQL |
| 2026-08-25 | Total project tests passed | 17/17 | Unit and integration tests |
| 2026-08-25 | Current statement coverage | 95% | 343 statements; not final-system coverage |
| 2026-08-25 | Test-suite runtime | 0.76 seconds | Local Apple Silicon environment |
| 2026-08-25 | Synthetic analytics rows | 114 | 6 departments, 12 employees, 24 reports, 72 items |
| 2026-08-25 | Synthetic expense total | $28,500.00 | Deterministic 2025 dataset |
| 2026-08-25 | Seed rerun counts | 6/12/24/72 | Idempotency verified |
| 2026-09-14 | DOC-001 canonical elements | 18 | Synthetic Markdown policy |
| 2026-09-14 | DOC-001 chunks | 7 | Structure-aware chunking |
| 2026-09-14 | Stored DOC-001 embeddings | 7 | BGE small v1.5, 384 dimensions |
| 2026-09-14 | Supported retrieval top score | 0.87207 | Paid Parental Leave section |
| 2026-09-14 | Unsupported API top score | 0.530257 | Below provisional 0.70 threshold |
| 2026-09-14 | RAG integration tests | 2/2 | Citation and abstention behavior |
| 2026-09-14 | FastAPI integration tests | 2/2 | Real API boundary with deterministic LLM |
| 2026-09-14 | Total project tests | 35/35 | Unit and integration tests |
| 2026-09-14 | Current statement coverage | 86% | 936 statements; not final-system coverage |
| 2026-09-14 | Full-suite runtime | 8.20 seconds | Local Apple Silicon environment |
| 2026-09-15 | Frozen retrieval cases | 18 | v0.2.0: 14 answerable, 4 unsupported |
| 2026-09-15 | Embedded corpus | 35/35 chunks | Six Markdown documents, BGE small v1.5 |
| 2026-09-15 | Dense Hit Rate@3 | 0.9286 | Frozen v0.2 dataset |
| 2026-09-15 | Dense Recall@3 | 0.8929 | Frozen v0.2 dataset |
| 2026-09-15 | Dense MRR@3 | 0.8929 | Frozen v0.2 dataset |
| 2026-09-15 | Dense Hit Rate@5 | 1.0000 | Frozen v0.2 dataset |
| 2026-09-15 | Dense Recall@5 | 0.9643 | Frozen v0.2 dataset |
| 2026-09-15 | Dense MRR@5 | 0.9107 | Frozen v0.2 dataset |
| 2026-09-15 | Unsupported abstention rate | 1.0000 | Four deterministic cases |
| 2026-09-15 | Citation hit rate | 0.9286 | Deterministic RAG Top-3 |
| 2026-09-15 | Complete citation recall rate | 0.8571 | Deterministic RAG Top-3 |
| 2026-09-15 | Total project tests | 42/42 | Unit and integration tests |
| 2026-09-15 | Current statement coverage | 81% | 1,239 statements |

## Evidence limitations

- Markdown is the only document format implemented and verified.
- Exact dense retrieval is evaluated only on a small synthetic 35-chunk corpus.
- The observed latency measurements are local and do not establish production
  performance or scalability.
- Deterministic RAG evaluation measures application control behavior, not real-LLM
  linguistic quality.
- Real Qwen behavior has been manually demonstrated on selected cases, including one
  malicious-document case, but not benchmarked across every golden case.
- The `0.70` threshold separates the current 18 cases but is not universally reliable.
- KNO-006 has incomplete conflict-evidence recall at Top-5.
- KNO-014 misses its expected section at Top-3 despite exceeding the threshold.
- PostgreSQL lexical retrieval and RRF hybrid retrieval are not implemented.
- Safe Text-to-SQL and LangGraph routing are not implemented.
- Structured logging and CI are not implemented.
- The FastAPI TestClient currently emits one upstream transition warning concerning
  `httpx` and `httpx2`.
- No production-readiness, deployment, security-completeness, accuracy-at-scale, or
  load-performance claim is supported.
# Verified Achievements Ledger

Last updated: 2026-09-14

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

## Implemented but not fully verified

- Module 0 knowledge validation is deferred pending review of the project owner's
  written notebook answers.
  - Module 2 implementation is verified, but the owner’s interview knowledge check has
  not yet been completed.

## Planned

## Planned

Multi-document evaluation, PostgreSQL lexical retrieval, RRF hybrid retrieval,
threshold calibration, malicious-document testing, SQL generation and `sqlglot`
validation, controlled LangGraph routing, structured application logging, CI, and
final portfolio packaging remain planned.

Docling PDF parsing, OCR, table extraction, reranking, MLflow, authentication, load
testing, and complete application containerization are optional under the revised
interview-ready scope.

## Resume eligible

None.

The verified items above are development foundations rather than sufficiently
substantial AI engineering accomplishments for a resume project bullet.

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

## Evidence limitations

- Markdown is the only document format currently implemented and verified.
- Docling parsing, PDF tables, and OCR are not implemented or verified.
- Dense retrieval has been demonstrated on one document and one supported question;
  no benchmark-level retrieval-quality claim is supported yet.
- The `0.70` abstention threshold is provisional and has not been calibrated.
- PostgreSQL lexical retrieval and RRF hybrid retrieval are not implemented.
- Retrieved text is labeled as untrusted evidence, but no malicious-document
  end-to-end test has passed yet.
- Safe Text-to-SQL and LangGraph routing are not implemented.
- Structured logging, CI, and complete application containerization are not
  implemented.
- Current coverage applies to the present implementation and does not establish
  production reliability.
- The current FastAPI TestClient emits one upstream deprecation warning concerning
  the transition from `httpx` to `httpx2`.
- The RAG and FastAPI changes must be committed and pushed before the vertical slice
  is preserved in the remote repository.

- No document ingestion, OCR, parsing, chunk generation, or embedding generation has
  been implemented.
- No retrieval-quality, RAG, routing, or generated-SQL measurement exists.
- Database results come from a local synthetic dataset, not production traffic.
- The PostgreSQL reader is currently a non-login permission role; application login
  credential provisioning remains planned for the Text-to-SQL module.
- Current coverage applies only to the implemented foundation.
- The repository has not yet been pushed to GitHub.

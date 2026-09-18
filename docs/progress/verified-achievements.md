# Verified Achievements Ledger

Last updated: 2026-09-18

This ledger records only capabilities supported by execution evidence. It does not
convert planned architecture into completed work.

## Implemented and verified

### Repository and Python foundation

- Created a Git repository on the `main` branch.
- Installed and executed CPython 3.12.14 on macOS ARM64.
- Initialized an installable package using a `src/` layout.
- Created a project-local virtual environment using `uv`.
- Generated and retained a reproducible `uv.lock` dependency lockfile.
- Built and installed package version `0.1.0`.
- Configured environment-prefixed settings through Pydantic Settings.
- Added a commit-safe `.env.example`.
- Excluded real `.env` files and common generated artifacts from Git.

### Automated quality foundation

- Configured Ruff linting and formatting.
- Configured Pyright in strict mode.
- Configured Pytest with branch-aware coverage.
- Installed repository pre-commit hooks.
- Verified Ruff, Pyright, Pytest, coverage, and pre-commit locally.
- Retained deterministic and integration test markers.
- Reached a current complete local baseline of 96 passing tests with 82% statement
  coverage.
- Completed the current full quality gate with zero Ruff errors and zero Pyright
  errors or warnings.

### Business domain and golden dataset

- Defined a fictional enterprise policy and expense-analytics domain.
- Created golden dataset v0.1 containing 15 routing, grounding, clarification, and
  refusal cases.
- Recorded eight policy-RAG, three Text-to-SQL, two clarification, and two refusal
  expectations.
- Implemented strict Pydantic validation with route-specific requirements.
- Rejected duplicate golden-case identifiers.
- Created frozen policy evaluation dataset v0.2 containing 18 cases:
  - 14 answerable cases.
  - Four unsupported cases.
  - Conflict-evidence cases.
  - A malicious-document prompt-injection fixture.

### PostgreSQL and pgvector foundation

- Ran PostgreSQL 17.11 and pgvector 0.8.6 locally through Docker Compose.
- Configured SQLAlchemy, Psycopg, connection pooling, and stale-connection checks.
- Configured Alembic and verified ordered migrations.
- Created six application tables in the `public` schema:
  - `documents`
  - `document_versions`
  - `processing_runs`
  - `chunks`
  - `embeddings`
  - `evaluation_runs`
- Created four business tables in the `analytics` schema:
  - `departments`
  - `employees`
  - `expense_reports`
  - `expense_items`
- Verified PostgreSQL `tsvector` and pgvector `vector` storage.
- Added foreign keys, uniqueness constraints, check constraints, and retrieval indexes.
- Verified migration downgrade and re-upgrade behavior.
- Passed eight PostgreSQL foundation integration tests.

### Synthetic analytics data and database security

- Created deterministic synthetic analytics data containing:
  - Six departments.
  - 12 employees.
  - 24 expense reports.
  - 72 expense items.
- Verified seed idempotency by preserving the same counts after repeated execution.
- Measured `$28,500.00` in total synthetic expenses.
- Created the non-login `enterprise_agent_analytics_reader` role.
- Granted only approved schema and table access.
- Applied column-level employee-table permissions.
- Verified that the role cannot read `annual_salary`.
- Verified that the role cannot modify analytics data.
- Verified database rejection of nonpositive expense amounts.

### Document ingestion and processing

- Created six original synthetic Markdown policy documents.
- Extracted and validated unique `DOC-\d{3}` document identifiers.
- Calculated SHA-256 content hashes.
- Persisted document identities and active document versions.
- Preserved document-version and chunk lineage.
- Verified unchanged-document idempotency.
- Implemented structure-aware Markdown chunking.
- Persisted 35 chunks across the six-document corpus.
- Verified that repeated unchanged ingestion does not create duplicate versions.

Only Markdown ingestion is currently implemented and verified.

### Embeddings and dense retrieval

- Integrated `BAAI/bge-small-en-v1.5`.
- Generated normalized 384-dimensional embeddings.
- Persisted 35 embeddings in PostgreSQL/pgvector.
- Verified embedding idempotency.
- Implemented exact dense cosine retrieval over active document versions.
- Retrieved the DOC-001 Paid Parental Leave section at rank one with similarity
  `0.87207` for the demonstrated supported question.
- Added a command-line path for embedding generation and dense search.

### Retrieval evaluation

- Implemented transparent retrieval metrics:
  - Hit Rate@K
  - Recall@K
  - Precision@K
  - Mean Reciprocal Rank
- Generated reproducible JSON evaluation reports.
- Measured exact dense Top-3:
  - Hit Rate: `0.9286`
  - Recall: `0.8929`
  - Precision: `0.3333`
  - MRR: `0.8929`
- Measured exact dense Top-5:
  - Hit Rate: `1.0000`
  - Recall: `0.9643`
  - Precision: `0.2143`
  - MRR: `0.9107`
- Preserved known retrieval limitations instead of removing difficult cases.
- Recorded incomplete KNO-006 conflict-evidence retrieval.
- Recorded the KNO-014 dense Top-3 miss.

### Lexical and RRF hybrid retrieval

- Reused the generated `chunks.search_vector` column and its GIN index.
- Implemented PostgreSQL full-text lexical retrieval.
- Preserved an initial multi-term AND baseline with Hit Rate@3 of `0.2143`.
- Implemented OR-term lexical retrieval.
- Measured lexical OR Top-3:
  - Hit Rate: `1.0000`
  - Recall: `1.0000`
  - Precision: `0.4286`
  - MRR: `0.7619`
- Implemented Reciprocal Rank Fusion over up to ten dense and ten lexical candidates.
- Deduplicated fused results by chunk ID.
- Avoided direct comparison of incompatible cosine and lexical raw scores.
- Measured RRF hybrid Top-3:
  - Hit Rate: `1.0000`
  - Recall: `0.9643`
  - Precision: `0.3571`
  - MRR: `0.8452`
- Verified through real PostgreSQL integration that hybrid retrieval recovers KNO-014
  within Top-3.
- Recorded that hybrid improved Top-3 coverage but did not improve dense MRR.
- Recorded that malicious DOC-007 content can rank first in selected retrieval modes.

### Grounded RAG

- Integrated local `qwen3.5:4b` through a provider-independent LLM interface.
- Implemented structured model output validation.
- Supplied retrieved document text as untrusted evidence.
- Added explicit prompt instructions that prohibit following document-embedded
  instructions.
- Converted model-selected evidence ranks into application-controlled citations.
- Implemented evidence-based abstention using a provisional `0.70` dense similarity
  threshold.
- Verified unsupported-question abstention without an LLM call.
- Measured deterministic Top-3 RAG behavior:
  - Supported-answer rate: `1.0000`
  - Unsupported abstention rate: `1.0000`
  - Citation hit rate: `0.9286`
  - Complete citation recall: `0.8571`
- Verified all four unsupported golden cases abstain without calling the LLM.
- Manually demonstrated safe behavior for a malicious-document case using local
  `qwen3.5:4b`.
- Returned a verified application-controlled citation to DOC-001 for the parental
  leave example.

### Safe Text-to-SQL

- Installed and locked SQLGlot 30.18.0.
- Implemented a narrow Text-to-SQL workflow for:
  “How much did Engineering spend on paid expense reports in 2025?”
- Required exactly one PostgreSQL `SELECT` statement.
- Rejected:
  - Writes and DDL.
  - Multiple statements.
  - CTEs.
  - Subqueries.
  - Wildcards.
  - Locking statements.
  - `SELECT INTO`.
  - Non-analytics schemas.
  - Non-allowlisted tables and columns.
  - Restricted employee and merchant fields.
  - Unknown functions.
  - Non-literal and excessive limits.
- Added mandatory `LIMIT 100` when the model omits a limit.
- Added an operation-specific semantic contract requiring:
  - The correct four tables.
  - Engineering department filtering.
  - Paid report-status filtering.
  - Inclusive 2025 and exclusive 2026 date bounds.
  - Filtering through `expense_reports.submitted_date`.
  - `COUNT(DISTINCT expense_reports.id)`.
  - `SUM(expense_items.amount)`.
  - Stable result aliases.
  - Department grouping.
- Preserved an incorrect real-model query using trip dates as a regression test.
- Executed validated SQL using:
  - A read-only transaction.
  - The least-privilege analytics reader role.
  - A three-second statement timeout.
  - Transaction rollback.
- Validated result count, department, report count, and monetary type before formatting.
- Verified local `qwen3.5:4b` produced SQL returning four reports and `$3,250.00`.
- Recorded 467 prompt tokens and 134 completion tokens for the demonstrated SQL run.
- Recorded `6,572.178 ms` for the standalone verified Text-to-SQL demonstration.
- Verified clarification and refusal paths avoid both SQL generation and execution.

### Controlled LangGraph workflow

- Installed and locked LangGraph 1.2.11.
- Defined a unified response model containing:
  - Route.
  - Answer.
  - Abstention.
  - Citations.
  - SQL and rows.
  - Retrieval score.
  - LLM model.
  - Token counts.
  - Total latency.
- Implemented deterministic routing across:
  - `policy_rag`
  - `text_to_sql`
  - `clarification`
  - `refusal`
- Compiled an explicit typed `StateGraph`.
- Added start, routing, execution, and terminal transitions.
- Preserved RAG and Text-to-SQL security controls outside the graph framework.
- Verified clarification and refusal without LLM, embedding, or business-query
  execution.
- Verified the RAG graph branch using real retrieval and deterministic generation.
- Verified the Text-to-SQL graph branch using real PostgreSQL and deterministic
  generation.
- Manually verified all four routes using local providers.
- Recorded the following real local workflow measurements:
  - RAG: `3,985.222 ms`
  - Text-to-SQL: `4,177.984 ms`
  - Clarification without LLM: `3.687 ms`
  - Refusal without LLM: `3.114 ms`

The workflow is deterministic orchestration, not an autonomous planning agent or an
LLM-based router.

### FastAPI service

- Exposed `GET /health`.
- Exposed `GET /ready` with a real PostgreSQL health check.
- Exposed unified `POST /api/v1/questions`.
- Enforced strict request models.
- Rejected unexpected request fields.
- Limited questions to 2,000 characters.
- Returned one unified response model for all four routes.
- Verified policy answer, policy abstention, analytics, clarification, and refusal
  behavior across the API boundary.
- Verified dependency replacement with deterministic providers during integration
  tests.
- Verified request-ID preservation through the API.

The PostgreSQL dependency is containerized through `compose.yaml`. The FastAPI
application itself is not containerized.

### Structured observability

- Added a dedicated observability package.
- Implemented machine-readable JSON logging.
- Added context-local request ID storage.
- Preserved safe caller-supplied `X-Request-ID` values.
- Replaced missing or unsafe request IDs.
- Returned `X-Request-ID` in API responses.
- Restored request context after completion.
- Logged request:
  - Event.
  - Request ID.
  - HTTP method.
  - Path.
  - Status.
  - Latency.
- Logged workflow:
  - Route.
  - Outcome.
  - Abstention.
  - Model identity.
  - Prompt tokens.
  - Completion tokens.
  - Retrieval top score.
  - Latency.
- Avoided logging:
  - Full user questions.
  - Generated SQL.
  - Result rows.
  - Retrieved evidence.
  - Credentials.
  - Database URLs.
- Passed five focused deterministic observability tests.
- Passed FastAPI request-ID propagation testing.

### Continuous integration

- Created `.github/workflows/ci.yml`.
- Configured execution on pushes to `main` and pull requests.
- Restricted workflow permissions to read-only repository contents.
- Added workflow concurrency cancellation.
- Used commit-pinned GitHub Actions.
- Installed a pinned `uv` release.
- Installed Python 3.12.
- Installed locked development dependencies.
- Ran Ruff lint.
- Verified Ruff formatting.
- Ran Pyright in strict mode.
- Ran deterministic tests with coverage.
- Excluded integration tests requiring local PostgreSQL.
- Added a syntactically valid, non-connecting CI database URL for tests that construct
  an engine without executing database operations.
- Pruned the `uv` cache after execution.
- Reproduced the CI environment locally:
  - 70 tests passed.
  - 26 integration tests were deselected.
  - Deterministic-subset coverage was 67%.
- Verified a successful GitHub-hosted Ubuntu workflow run for commit `93bacd1`.

The first remote workflow run exposed the missing CI database setting. The failure was
reproduced locally, corrected, committed, and followed by a green run.

## Current complete verification baseline

The latest complete local quality gate produced:

```text
96 passed
82% statement coverage
0 Ruff errors
0 Pyright errors
0 Pyright warnings
All configured pre-commit hooks passed
```

The complete suite includes 26 real integration tests.

The latest deterministic CI-equivalent run produced:

```text
70 passed
26 integration tests deselected
67% deterministic-subset statement coverage
```

The remote GitHub Actions workflow completed successfully.

## Resume-eligible claims

The following claims are supported when stated with their boundaries.

### Retrieval evaluation

Implemented and evaluated exact dense, PostgreSQL lexical, and RRF hybrid retrieval
over a frozen 18-case synthetic dataset, measuring Hit Rate@K, Recall@K, Precision@K,
and MRR.

Do not claim that hybrid improved overall ranking quality. It improved Top-3 evidence
coverage relative to dense retrieval but produced lower MRR.

### Grounded RAG

Implemented a grounded local RAG workflow with evidence thresholds,
application-controlled citations, unsupported-question abstention, structured model
output, and prompt-injection controls.

Do not describe the evaluation as demonstrating general model accuracy or
production-scale reliability.

### Safe Text-to-SQL

Implemented SQLGlot AST validation, schema and column allowlists, operation-specific
semantic checks, result validation, read-only transactions, statement timeouts, and a
least-privilege PostgreSQL role.

Describe this as one controlled aggregate operation. Do not describe it as unrestricted
natural-language database access.

### Controlled LangGraph workflow

Implemented deterministic LangGraph orchestration across grounded RAG, safe
Text-to-SQL, clarification, and refusal paths.

Do not describe it as an autonomous agent, multi-agent system, or LLM-based router.

### Backend, observability, and CI

Implemented a unified FastAPI endpoint, structured request-correlated JSON logging,
strict type checking, deterministic and integration testing, and a remotely verified
GitHub Actions workflow.

Do not describe the service as production deployed, authenticated, load tested, or
fully containerized.

## Implemented but not fully verified

- The project owner’s complete concept and interview knowledge review remains pending.
- Final resume bullets remain pending until the knowledge review is completed.

## Deferred scope

The following capabilities are optional or intentionally deferred:

- PDF and Office-document parsing.
- OCR.
- Table extraction.
- Cross-encoder reranking.
- MLflow.
- Authentication and authorization.
- Rate limiting.
- Load testing.
- Full application containerization.
- Cloud deployment.
- Kubernetes.
- Persistent LangGraph checkpoints.
- Conversation memory.
- External tracing.

## Evidence limitations

- The policy corpus contains six synthetic Markdown documents and 35 chunks.
- Markdown is the only verified ingestion format.
- The retrieval evaluation contains 18 synthetic cases.
- Exact dense retrieval has not been evaluated at production scale.
- The provisional `0.70` threshold is corpus-specific and is not universally reliable.
- KNO-006 has incomplete conflict-evidence recall.
- KNO-014 is missed by dense retrieval at Top-3.
- Lexical and RRF hybrid retrieval are evaluated offline but are not used by the API
  answer path.
- RRF scores cannot use the current cosine-based abstention threshold.
- Malicious content can rank highly; ranking is not treated as a security boundary.
- Deterministic RAG evaluation measures application behavior more than free-form model
  quality.
- Real Qwen behavior was demonstrated only on selected cases.
- Text-to-SQL supports one explicitly approved aggregate operation.
- The v0.1 SQL cases referencing 2026 remain specification-only because the analytics
  fixture contains 2025 records.
- One successful real Text-to-SQL execution does not establish general SQL-generation
  accuracy.
- LangGraph routing is deterministic and allowlist-based.
- The graph is compiled per invocation.
- Persistent checkpoints and conversation memory are deferred.
- Installed LangGraph dependencies include checkpoint and LangSmith packages, but this
  project does not use persistence or external tracing.
- Operational logs do not replace metrics aggregation, alerting, or distributed
  tracing.
- The API has no authentication, authorization, rate limiting, or TLS termination.
- The FastAPI application is not containerized.
- GitHub Actions does not execute PostgreSQL integration tests.
- Latency values were measured locally and do not establish production performance.
- The project has not been load tested or deployed to a production environment.
- No production-readiness, security-completeness, accuracy-at-scale, or
  general-reliability claim is supported.

## Selected recorded measurements

| Date | Measurement | Result | Context |
|---|---|---:|---|
| 2026-08-17 | Initial smoke tests | 1/1 | Generated package scaffold |
| 2026-08-17 | Initial coverage | 100% | Two executable scaffold statements |
| 2026-08-19 | Golden dataset cases | 15 | Version 0.1 specification |
| 2026-08-19 | Project tests | 9/9 | Foundation and golden-data validation |
| 2026-08-25 | PostgreSQL version | 17.11 | Local Docker Compose |
| 2026-08-25 | pgvector version | 0.8.6 | PostgreSQL extension |
| 2026-08-25 | Database tables | 10 | Six public and four analytics tables |
| 2026-08-25 | Synthetic analytics rows | 114 | 6 departments, 12 employees, 24 reports, 72 items |
| 2026-08-25 | Synthetic expense total | $28,500.00 | Deterministic fixture |
| 2026-09-14 | Embedded corpus | 35/35 chunks | BGE-small v1.5, 384 dimensions |
| 2026-09-14 | Supported retrieval score | 0.87207 | DOC-001 parental-leave example |
| 2026-09-15 | Frozen policy cases | 18 | 14 answerable and four unsupported |
| 2026-09-15 | Dense Hit Rate@3 | 0.9286 | Frozen v0.2 |
| 2026-09-15 | Dense Recall@3 | 0.8929 | Frozen v0.2 |
| 2026-09-15 | Dense MRR@3 | 0.8929 | Frozen v0.2 |
| 2026-09-15 | Lexical Hit Rate@3 | 1.0000 | OR-term PostgreSQL retrieval |
| 2026-09-15 | Lexical MRR@3 | 0.7619 | OR-term PostgreSQL retrieval |
| 2026-09-15 | Hybrid Hit Rate@3 | 1.0000 | RRF fusion |
| 2026-09-15 | Hybrid Recall@3 | 0.9643 | RRF fusion |
| 2026-09-15 | Hybrid MRR@3 | 0.8452 | RRF fusion |
| 2026-09-15 | Unsupported abstention rate | 1.0000 | Four deterministic cases |
| 2026-09-15 | Citation hit rate | 0.9286 | Deterministic RAG |
| 2026-09-15 | Complete citation recall | 0.8571 | Deterministic RAG |
| 2026-09-17 | SQLGlot version | 30.18.0 | PostgreSQL AST validation |
| 2026-09-17 | Verified SQL result | 4 reports / $3,250.00 | Paid Engineering reports in 2025 |
| 2026-09-17 | SQL model tokens | 467 / 134 | Prompt / completion |
| 2026-09-17 | Standalone SQL latency | 6,572.178 ms | Local end-to-end execution |
| 2026-09-17 | LangGraph version | 1.2.11 | Controlled orchestration |
| 2026-09-17 | Workflow RAG latency | 3,985.222 ms | Local BGE-small and Qwen |
| 2026-09-17 | Workflow SQL latency | 4,177.984 ms | Local Qwen and PostgreSQL |
| 2026-09-17 | Clarification latency | 3.687 ms | No LLM |
| 2026-09-17 | Refusal latency | 3.114 ms | No LLM |
| 2026-09-17 | Complete project tests | 96/96 | Local full suite |
| 2026-09-17 | Complete statement coverage | 82% | 1,726 statements |
| 2026-09-17 | Deterministic CI tests | 70/70 | 26 integration tests excluded |
| 2026-09-17 | CI-subset coverage | 67% | Service-free deterministic run |
| 2026-09-17 | GitHub Actions | Passed | Commit `93bacd1`, Ubuntu runner |
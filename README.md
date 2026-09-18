# Enterprise Knowledge and Analytics Agent

A security-focused AI engineering portfolio project combining grounded enterprise
document question answering with controlled, read-only natural-language analytics.

> This repository uses a fictional organization, original synthetic documents, and
> synthetic operational data. It does not represent work performed for an employer
> or client.

## Why this project exists

Enterprise knowledge is commonly divided between:

- Unstructured policy documents.
- Structured operational databases.

Users should be able to ask questions such as:

- How many weeks of paid parental leave are available?
- What receipts are required for travel expenses?
- Can an employee work remotely from another state?
- How much did Engineering spend on paid expense reports in 2025?

A general chatbot is insufficient for these requests. It may hallucinate policy
details, ignore document versions, follow instructions embedded in retrieved
documents, expose restricted fields, or generate unsafe SQL.

This project therefore uses a controlled workflow that routes each request to one of
four paths:

1. Grounded RAG for policy questions.
2. Restricted Text-to-SQL for an explicitly approved analytics operation.
3. Clarification when required details are missing.
4. Refusal when the request is destructive or asks for restricted data.

## Current verified capabilities

The following capabilities have been implemented and verified:

- Deterministic Markdown ingestion with SHA-256 content hashing.
- Document identity, version lineage, and idempotent persistence.
- Structure-aware chunking across six synthetic policy documents.
- Normalized 384-dimensional `BAAI/bge-small-en-v1.5` embeddings.
- PostgreSQL 17 with pgvector 0.8.6.
- Exact dense retrieval using cosine similarity.
- PostgreSQL full-text lexical retrieval.
- Reciprocal Rank Fusion over dense and lexical candidate lists.
- Frozen retrieval and RAG evaluation datasets.
- Grounded RAG with application-controlled citations and abstention.
- Prompt-injection handling that treats retrieved documents as untrusted evidence.
- SQLGlot-based PostgreSQL AST validation.
- Allowlisted tables and columns for Text-to-SQL.
- Database-enforced read-only analytics permissions.
- Operation-specific semantic SQL validation.
- Deterministic LangGraph routing.
- FastAPI health, readiness, and unified question endpoints.
- Structured JSON logs with request/correlation IDs.
- Route, outcome, model, token, score, and latency logging.
- Ruff, Pyright strict mode, Pytest, coverage, and pre-commit checks.
- GitHub Actions continuous integration using locked dependencies.

The complete local quality gate currently passes **96 tests** with **82% statement
coverage**.

GitHub Actions separately runs the deterministic test subset: **70 tests pass** and
**26 PostgreSQL integration tests are intentionally excluded**.

## System architecture

```mermaid
flowchart TD
    U["Client"] --> API["FastAPI API"]
    API --> RID["Request ID and JSON logging"]
    RID --> ROUTER["Deterministic LangGraph router"]

    ROUTER -->|Policy| RAG["Grounded RAG"]
    ROUTER -->|Approved analytics| SQL["Safe Text-to-SQL"]
    ROUTER -->|Incomplete| CLARIFY["Clarification"]
    ROUTER -->|Unsafe| REFUSE["Refusal"]

    RAG --> RETRIEVE["Dense retrieval and evidence threshold"]
    RETRIEVE --> PG["PostgreSQL and pgvector"]
    RAG --> OLLAMA["Local Ollama model"]

    SQL --> VALIDATE["SQLGlot and semantic contract"]
    VALIDATE --> READER["Read-only analytics role"]
    READER --> PG
    SQL --> OLLAMA
```

LangGraph provides explicit orchestration, but it is not the security boundary.
Safety remains enforced by application routing, evidence thresholds, SQL validation,
result validation, database permissions, transaction controls, and allowlists.

See [`docs/architecture/system-architecture.md`](docs/architecture/system-architecture.md)
for the detailed architecture.

## Verified workflow routes

| Route | Purpose | LLM used? | Database execution? |
|---|---|---:|---:|
| `policy_rag` | Answer supported policy questions with citations | Yes, after sufficient evidence | Retrieval only |
| `text_to_sql` | Execute one approved aggregate analytics operation | Yes | Yes, read-only |
| `clarification` | Request missing analytics details | No | No |
| `refusal` | Reject destructive or restricted-data requests | No | No |

Routing is deterministic and allowlist-based. It is not an autonomous agent or an
LLM-based intent classifier.

## Retrieval evaluation

The frozen v0.2 policy dataset contains 18 cases:

- 14 answerable questions.
- 4 unsupported questions.
- Conflict-evidence cases.
- A malicious-document prompt-injection fixture.

| Retrieval system | Hit Rate@3 | Recall@3 | Precision@3 | MRR@3 |
|---|---:|---:|---:|---:|
| Exact dense | 0.9286 | 0.8929 | 0.3333 | 0.8929 |
| PostgreSQL lexical OR | 1.0000 | 1.0000 | 0.4286 | 0.7619 |
| RRF hybrid | 1.0000 | 0.9643 | 0.3571 | 0.8452 |

Hybrid retrieval improved Top-3 evidence coverage relative to dense retrieval but did
not improve overall MRR. The current API answer path still uses dense retrieval because
hybrid scores require separate abstention calibration.

## Grounded RAG controls

The RAG path:

1. Embeds the user question.
2. Retrieves relevant active document chunks from pgvector.
3. Compares the top similarity score with a provisional `0.70` threshold.
4. Abstains without calling the LLM when evidence is insufficient.
5. Supplies retrieved text to the model as untrusted evidence.
6. Requires structured model output.
7. Converts model-selected evidence ranks into application-controlled citations.

The frozen deterministic evaluation measured:

- Supported-answer rate: `1.0000`.
- Unsupported abstention rate: `1.0000`.
- Citation hit rate: `0.9286`.
- Complete citation recall: `0.8571`.

These results apply only to the small synthetic evaluation corpus.

## Safe Text-to-SQL controls

The current Text-to-SQL path supports one explicitly approved operation:

> How much did Engineering spend on paid expense reports in 2025?

Generated SQL must satisfy both general and operation-specific controls.

General SQL validation rejects:

- Non-`SELECT` statements.
- Multiple statements.
- DDL and write operations.
- CTEs and subqueries.
- Wildcards.
- Locking queries.
- `SELECT INTO`.
- Non-analytics schemas.
- Non-allowlisted tables or columns.
- Restricted employee and merchant fields.
- Unknown functions.
- Non-literal or excessive limits.

The validator adds `LIMIT 100` when no limit is supplied.

The approved operation also requires:

- All four required analytics tables.
- The `Engineering` department filter.
- The `paid` report-status filter.
- Inclusive 2025 start and exclusive 2026 end dates.
- Date filtering through `expense_reports.submitted_date`.
- `COUNT(DISTINCT expense_reports.id)` as `report_count`.
- `SUM(expense_items.amount)` as `total_usd`.
- Department grouping.
- A validated one-row result shape.

Execution uses:

- A read-only PostgreSQL transaction.
- The non-login `enterprise_agent_analytics_reader` role.
- Column-level protection for restricted employee data.
- A three-second statement timeout.
- Transaction rollback after execution.

The verified result is four paid Engineering reports totaling `$3,250.00`.

This is a narrow safety-focused demonstration, not unrestricted natural-language
database access.

## Technology stack

- Python 3.12
- FastAPI
- LangGraph
- Pydantic
- SQLAlchemy
- Psycopg
- Alembic
- PostgreSQL 17
- pgvector 0.8.6
- SQLGlot 30.18.0
- Sentence Transformers
- `BAAI/bge-small-en-v1.5`
- Ollama with local `qwen3.5:4b`
- Docker Compose
- `uv`
- Ruff
- Pyright
- Pytest
- GitHub Actions

## Repository organization

```text
data/
  documents/              Synthetic Markdown policy corpus
  golden/                 Frozen evaluation datasets

docs/
  adr/                    Architecture decisions
  architecture/           System architecture
  domain/                 Synthetic business-domain specification
  interview/              Cumulative interview question bank
  progress/               Progress and verified-evidence ledgers
  security/               Security controls and limitations

migrations/               Alembic database migrations

src/enterprise_knowledge_analytics_agent/
  analytics/              Routing, SQL validation, execution, and result formatting
  api/                    FastAPI application and dependencies
  evaluation/             Golden-data loading and evaluation
  ingestion/              Markdown parsing and persistence
  observability/          Structured logging and request context
  persistence/            Database engine, models, and analytics seed data
  processing/             Structure-aware chunking
  rag/                    Grounded answer generation
  retrieval/              Dense, lexical, and hybrid retrieval
  workflow/               LangGraph routing and orchestration

tests/
  integration/            PostgreSQL and API integration tests
  test_*.py               Deterministic unit and component tests
```

## Local development setup

### Prerequisites

Install:

- Git.
- Python 3.12.
- `uv`.
- Docker with Docker Compose.
- Ollama for real local model execution.

The deterministic unit tests do not require PostgreSQL or Ollama.

### Clone and install

```bash
git clone \
  https://github.com/Dev-Divyendh/enterprise-knowledge-analytics-agent.git

cd enterprise-knowledge-analytics-agent

uv sync --locked --dev
```

### Configure the environment

Create `.env` from the commit-safe example:

```bash
if [ ! -f .env ]; then
  cp .env.example .env
fi
```

The example contains local-only development credentials. Replace them before using
the project outside an isolated development environment. Never commit real secrets.

### Start PostgreSQL and pgvector

```bash
docker compose up -d postgres
docker compose ps
```

`compose.yaml` containerizes the PostgreSQL/pgvector dependency. The FastAPI
application itself runs directly through `uv`; complete application containerization
is intentionally deferred.

### Apply migrations

```bash
uv run alembic upgrade head
uv run alembic current
```

### Seed synthetic analytics data

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

The seed operation is deterministic and idempotent.

### Prepare the policy corpus

Ingest a Markdown document:

```bash
uv run python -m \
  enterprise_knowledge_analytics_agent.ingestion \
  data/documents/DOC-001-parental-leave-policy.md
```

Generate missing embeddings for the ingested document:

```bash
uv run python -m \
  enterprise_knowledge_analytics_agent.retrieval \
  embed DOC-001
```

Repeat these two operations for each document under `data/documents/`. Ingestion and
embedding generation are idempotent.

### Run dense retrieval manually

```bash
uv run python -m \
  enterprise_knowledge_analytics_agent.retrieval \
  search "How many weeks of paid parental leave are available?" \
  --top-k 3
```

### Run grounded RAG manually

Ensure Ollama is running and the configured local model is available. Then run:

```bash
uv run python -m \
  enterprise_knowledge_analytics_agent.rag \
  "How many weeks of paid parental leave are available?"
```

### Run dense retrieval evaluation

```bash
uv run python -m \
  enterprise_knowledge_analytics_agent.evaluation \
  data/golden/v0.2/cases.json \
  --top-k 3 \
  --output reports/dense-top3.json
```

Evaluation writes a reproducible JSON report and prints the calculated metrics.

## Run the API

Start the local FastAPI application:

```bash
uv run uvicorn \
  enterprise_knowledge_analytics_agent.api.app:app \
  --host 127.0.0.1 \
  --port 8000
```

Interactive API documentation is available at:

```text
http://127.0.0.1:8000/docs
```

### Health check

```bash
curl http://127.0.0.1:8000/health
```

### Database readiness

```bash
curl http://127.0.0.1:8000/ready
```

### Policy question

```bash
curl -s \
  -X POST \
  http://127.0.0.1:8000/api/v1/questions \
  -H 'Content-Type: application/json' \
  -H 'X-Request-ID: readme-policy-demo' \
  -d '{
    "question": "How many weeks of paid parental leave are available?"
  }'
```

### Approved analytics question

```bash
curl -s \
  -X POST \
  http://127.0.0.1:8000/api/v1/questions \
  -H 'Content-Type: application/json' \
  -H 'X-Request-ID: readme-analytics-demo' \
  -d '{
    "question": "How much did Engineering spend on paid expense reports in 2025?"
  }'
```

### Clarification route

```bash
curl -s \
  -X POST \
  http://127.0.0.1:8000/api/v1/questions \
  -H 'Content-Type: application/json' \
  -d '{
    "question": "How much did Sales spend?"
  }'
```

### Refusal route

```bash
curl -s \
  -X POST \
  http://127.0.0.1:8000/api/v1/questions \
  -H 'Content-Type: application/json' \
  -d '{
    "question": "Delete all expense records older than two years."
  }'
```

Every API response includes an `X-Request-ID` header. A safe caller-supplied ID is
preserved; missing or unsafe IDs are replaced.

## Observability

The API emits structured JSON logs for:

- Request completion.
- Request failure.
- Workflow completion.
- Request ID.
- HTTP method and path.
- HTTP status.
- Selected route.
- Outcome and abstention.
- LLM model.
- Prompt and completion token counts.
- Retrieval top score.
- Request and workflow latency.

Logs intentionally exclude:

- Full user questions.
- Generated SQL.
- Database rows.
- Retrieved evidence text.
- Credentials and connection strings.

This reduces accidental disclosure while retaining useful operational metadata.

## Testing

### Complete local quality gate

PostgreSQL must be running, migrations must be current, and the integration-test
environment must be configured.

```bash
uv run ruff format --check .
uv run ruff check .
uv run pyright

uv run pytest \
  --cov \
  --cov-report=term-missing

uv run pre-commit run --all-files
git diff --check
```

Current verified result:

```text
96 passed
82% statement coverage
0 Ruff errors
0 Pyright errors or warnings
All pre-commit hooks passed
```

### Deterministic CI-equivalent suite

This suite does not connect to PostgreSQL:

```bash
EKA_DATABASE_URL='postgresql+psycopg://ci_user:ci_password@localhost:5432/ci_placeholder' \
uv run --frozen pytest \
  -m "not integration" \
  --cov \
  --cov-report=term-missing
```

Current verified result:

```text
70 passed
26 integration tests deselected
67% statement coverage for the deterministic subset
```

## Continuous integration

`.github/workflows/ci.yml` runs on pushes to `main` and on pull requests.

The workflow:

1. Checks out the repository using a commit-pinned action.
2. Installs a pinned `uv` release.
3. Installs Python 3.12.
4. Synchronizes locked development dependencies.
5. Runs Ruff lint.
6. Verifies Ruff formatting.
7. Runs Pyright in strict mode.
8. Runs the deterministic non-integration test suite with coverage.
9. Prunes the CI cache.

The workflow was remotely verified on GitHub Actions after commit `93bacd1`.

PostgreSQL integration tests remain part of the complete local gate and are not
currently executed in GitHub Actions.

## Security boundaries

Implemented controls include:

- Synthetic data only.
- Strict Pydantic request and structured-output models.
- Maximum question length of 2,000 characters.
- Deterministic allowlist-based routing.
- Evidence-threshold abstention.
- Retrieved documents treated as untrusted data.
- Application-controlled citations.
- SQL AST validation.
- Table and column allowlists.
- Restricted-field rejection.
- Operation-specific SQL semantic validation.
- Mandatory result limits.
- Read-only transactions.
- Least-privilege PostgreSQL role.
- Column-level employee-data permissions.
- Statement timeouts.
- Result-shape validation.
- Request-ID validation.
- Safe structured logging.
- No raw questions, SQL, rows, evidence, or credentials in operational logs.

See
[`docs/security/security-and-limitations.md`](docs/security/security-and-limitations.md)
for the threat boundaries and known limitations.

## Known limitations

- Only Markdown ingestion has been implemented and verified.
- OCR, PDF parsing, table extraction, and multi-format ingestion are deferred.
- The corpus contains only 35 chunks from six synthetic documents.
- Dense retrieval is exact rather than evaluated at production scale.
- The `0.70` abstention threshold is provisional and corpus-specific.
- KNO-006 has incomplete conflict-evidence recall.
- KNO-014 is missed by dense retrieval at Top-3.
- Lexical and RRF retrieval are evaluated offline but are not used by the API answer
  path.
- Malicious content can rank highly, so retrieval ranking alone is not a security
  control.
- Text-to-SQL supports one explicitly allowlisted aggregate operation.
- Real-model behavior has been manually demonstrated on selected cases, not
  benchmarked across every golden case.
- LangGraph routing is deterministic rather than autonomous or LLM-driven.
- Workflow checkpoints, conversation memory, and external tracing are deferred.
- Authentication, authorization at the API boundary, rate limiting, and TLS
  termination are not implemented.
- The FastAPI application is not containerized.
- GitHub Actions does not currently run PostgreSQL integration tests.
- Load testing, cloud deployment, MLflow, reranking, and production monitoring are
  deferred.
- Local measurements do not establish production reliability, security completeness,
  scalability, or general model accuracy.

## Verified measurements

Selected measured results:

- Six synthetic policy documents.
- 35 structure-aware chunks.
- 35 normalized embeddings.
- 18 frozen policy evaluation cases.
- 114 synthetic analytics rows.
- `$28,500.00` total synthetic expenses.
- 96 passing project tests.
- 82% full-suite statement coverage.
- 70 passing deterministic CI tests.
- 0 Ruff failures.
- 0 Pyright errors or warnings.
- Successful GitHub Actions execution.
- Real RAG workflow latency: `3,985.222 ms`.
- Real Text-to-SQL workflow latency: `4,177.984 ms`.
- Clarification latency without an LLM: `3.687 ms`.
- Refusal latency without an LLM: `3.114 ms`.

Detailed historical evidence is recorded in
[`docs/progress/verified-achievements.md`](docs/progress/verified-achievements.md).

## Evidence policy

Capabilities are tracked separately as:

1. Planned.
2. Implemented but not fully verified.
3. Implemented and verified.
4. Resume eligible.

A capability is treated as resume eligible only after:

- The implementation exists.
- Relevant checks pass.
- Execution evidence is recorded.
- Reproduction instructions exist.
- Limitations are documented.
- The design and trade-offs can be explained accurately.

Planned architecture is not presented as completed work.

## Deferred scope

The following capabilities are intentionally optional or deferred:

- PDF and Office-document parsing.
- OCR and table extraction.
- Cross-encoder reranking.
- MLflow.
- Authentication.
- Rate limiting.
- Load testing.
- Full application containerization.
- Cloud deployment.
- Kubernetes.
- Persistent LangGraph checkpoints.
- Conversation memory.

## Project documentation

- [System architecture](docs/architecture/system-architecture.md)
- [Security and limitations](docs/security/security-and-limitations.md)
- [Domain specification](docs/domain/domain-specification.md)
- [PostgreSQL and pgvector ADR](docs/adr/0001-postgresql-pgvector.md)
- [Project progress](docs/progress/project-progress.md)
- [Verified achievements](docs/progress/verified-achievements.md)
- [Interview question bank](docs/interview/question-bank.md)

## License and data

A license will be selected before public release.

All example business documents and operational records are synthetic. They must not be
interpreted as real organizational policies, employee records, financial data, or
legal guidance.
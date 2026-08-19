# Project Progress Tracker

Last updated: 2026-08-17

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
| 1 | Repository foundation | In progress | Local command outputs and smoke test |
| 1 | Business domain and golden dataset v0 | Planned | None |
| 2 | PostgreSQL and pgvector foundation | Planned | None |
| 3 | Document ingestion | Planned | None |
| 4 | Processing and chunking | Planned | None |
| 5 | Embeddings and vector indexing | Planned | None |
| 6 | Retrieval experiments | Planned | None |
| 7 | Grounded RAG | Planned | None |
| 8 | Safe Text-to-SQL | Planned | None |
| 9 | Controlled LangGraph workflow | Planned | None |
| 10 | FastAPI and containerized service | Planned | None |
| 11 | Golden evaluation and MLflow | Planned | None |
| 12 | Focused observability | Planned | None |
| 13 | Focused testing and security | Planned | None |
| 14 | CI and portfolio packaging | Planned | None |

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

## Current blockers

None.

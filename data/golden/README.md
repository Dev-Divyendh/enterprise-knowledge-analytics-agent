# Golden Evaluation Data

This directory contains versioned expected behaviors for the Enterprise Knowledge and
Analytics Agent.

## Version lifecycle

- **Specification only:** Questions and expected behavior are defined, but required
  documents or analytics fixtures may not exist yet.
- **Frozen:** All required sources and fixtures exist. A frozen version is not edited
  during baseline-versus-candidate comparisons.
- **Retired:** Retained for lineage but no longer used for release evaluation.

The current `v0.1/cases.json` dataset is specification-only.

## Current v0.1 coverage

- 15 total cases.
- 8 policy-RAG routes.
- 3 Text-to-SQL routes.
- 2 clarification routes.
- 2 refusal routes.
- Direct policy, table, OCR, conflict, unsupported, prompt-injection, approved
  analytics, ambiguous analytics, destructive, and restricted-data cases.

## Change policy

Do not modify a frozen dataset to make a system result look better. Corrections require
a documented reason, and material changes create a new dataset version.

Expected SQL result references will be resolved after deterministic analytics fixtures
are created in Module 2.
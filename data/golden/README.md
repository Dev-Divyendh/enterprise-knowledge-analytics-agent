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

## Frozen retrieval dataset v0.2

`v0.2/cases.json` is the frozen policy-RAG evaluation dataset.

- 18 total cases.
- 14 answerable cases.
- Four unsupported cases.
- Direct policy, reimbursement, security, conflict, abstention, and
  malicious-document behavior.
- Expected document and section labels for retrieval and citation evaluation.
- Used unchanged for exact-dense Top-3 and Top-5 measurements.

Generated reports are stored under `reports/evaluation/`. The frozen dataset must not
be edited to improve measured results; material corrections require a new version.

## Change policy

Do not modify a frozen dataset to make a system result look better. Corrections require
a documented reason, and material changes create a new dataset version.

Expected SQL result references will be resolved after deterministic analytics fixtures
are created in Module 2.
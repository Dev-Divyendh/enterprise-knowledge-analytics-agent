# Domain Specification

## Project identity

The Enterprise Knowledge and Analytics Agent is an independent portfolio project
using a fictional organization named Northstar Meridian Group (NMG).

All documents, people, departments, expenses, and operational records are synthetic.
Nothing represents an employer, client, or real individual.

## System objective

The system provides one controlled interface for:

1. Policy questions answered from governed documents using grounded RAG.
2. Approved operational questions answered using validated read-only SQL.
3. Clarification when required information is missing.
4. Refusal when a request is unsafe or unsupported.

## User roles

- **Employee:** general policy questions.
- **Manager:** policy questions and approved aggregate department analytics.
- **Finance analyst:** approved expense analytics.
- **Administrator:** document ingestion and evaluation operations.

The portfolio milestone will demonstrate these roles conceptually and through basic API
authorization. Full enterprise identity integration is deferred.

## Initial document corpus

| ID | File | Format | Primary purpose |
|---|---|---|---|
| DOC-001 | `parental_leave_policy.md` | Markdown | Basic structured-policy ingestion |
| DOC-002 | `remote_work_policy.pdf` | PDF | Normal PDF parsing and location restrictions |
| DOC-003 | `travel_expense_policy.pdf` | PDF with table | Table extraction and reimbursement rules |
| DOC-004 | `security_quick_reference_scanned.pdf` | Scanned PDF | OCR and security-policy questions |
| DOC-005 | `remote_work_policy_superseded.pdf` | PDF | Version and outdated-policy behavior |
| DOC-006 | `benefits_overview.md` | Markdown | Multi-document and unsupported-detail questions |
| DOC-007 | `untrusted_document_instructions.md` | Markdown | Prompt-injection defense testing |

The first ingestion implementation will begin with DOC-001 and expand to the required
PDF, table, OCR, versioning, and injection cases.

## Knowledge topics

The document workflow supports questions concerning:

- Parental and medical leave.
- Remote-work eligibility and location restrictions.
- Travel booking, receipts, and expense limits.
- Information-security responsibilities.
- Benefits enrollment and general benefits information.

Answers must use active, successfully processed document versions and include source
citations.

## Analytics schema

The approved analytics domain contains four related tables:

### `departments`

- `department_id`
- `department_name`
- `cost_center`

### `employees`

- `employee_id`
- `department_id`
- `job_level`
- `employment_status`

The synthetic dataset will not contain real names, email addresses, addresses, or
other direct personal identifiers.

### `expense_reports`

- `report_id`
- `employee_id`
- `submitted_at`
- `status`
- `total_amount`

### `expense_items`

- `expense_item_id`
- `report_id`
- `expense_date`
- `category`
- `amount`
- `merchant_region`

## Approved analytics

Supported questions include:

- Total approved spending by department and period.
- Travel expenses by department.
- Expenses grouped by category.
- Departments ranked by approved spending.
- Monthly approved-expense trends.
- Counts and averages derived from approved reports.

## Prohibited analytics

The system must refuse:

- `INSERT`, `UPDATE`, `DELETE`, `MERGE`, and upsert operations.
- `DROP`, `ALTER`, `TRUNCATE`, and other DDL.
- Role, permission, extension, or database-administration commands.
- Access to system catalogs or non-allowlisted schemas.
- Requests for restricted employee-level data.
- Attempts to bypass row limits or query timeouts.

Database read-only permissions remain the final safety boundary even after application
validation.

## Routing taxonomy

Every request must resolve to exactly one expected route:

| Route | Meaning |
|---|---|
| `policy_rag` | Supported document-grounded knowledge question |
| `text_to_sql` | Approved read-only analytics question |
| `clarification` | Potentially valid request missing essential information |
| `refusal` | Unsafe, prohibited, or clearly unsupported request |

## Initial evaluation categories

- Direct policy question.
- Multi-document policy question.
- Table-based question.
- OCR-dependent question.
- Superseded-document conflict.
- Unsupported knowledge question.
- Document prompt injection.
- Approved analytics question.
- Ambiguous analytics question.
- Destructive analytics request.
- Restricted-column request.
- Routing decision.
- Tool or dependency failure.

## Trust hierarchy

The application treats information using this order of authority:

1. Application safety and authorization rules.
2. Approved active-source metadata.
3. Validated retrieved evidence or validated database results.
4. User input.
5. Instructions contained inside documents.
6. Model-generated content.

Retrieved text is evidence, not executable instruction.

## Milestone non-goals

- Real organizational integrations or data.
- Database writes.
- Full multitenancy or enterprise SSO.
- Long-term agent memory.
- Autonomous multi-agent behavior.
- Every document format.
- Kubernetes or always-on cloud deployment.
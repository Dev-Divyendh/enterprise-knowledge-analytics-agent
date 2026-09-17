from decimal import Decimal
from time import perf_counter
from typing import Any

import sqlglot
from sqlalchemy import Engine
from sqlglot import expressions as exp

from enterprise_knowledge_analytics_agent.analytics.domain import (
    AnalyticsAnswer,
    SQLProposal,
)
from enterprise_knowledge_analytics_agent.analytics.sql import (
    SQLValidationError,
    execute_validated_sql,
    validate_sql,
)
from enterprise_knowledge_analytics_agent.rag.providers import LLMProvider

APPROVED_ENGINEERING_QUESTION = "How much did Engineering spend on paid expense reports in 2025?"
AMBIGUOUS_QUARTER_QUESTION = "How much did Engineering spend last quarter?"
AMBIGUOUS_EXPENSE_QUESTION = "Tell me about expenses."
DESTRUCTIVE_REQUEST = "Delete all expense records older than two years."
RESTRICTED_DATA_REQUEST = (
    "List every employee and the merchants where they used their expense cards."
)

QUARTER_CLARIFICATION_MESSAGE = (
    "Please specify the quarter or exact reporting dates for the Engineering expense analysis."
)

EXPENSE_CLARIFICATION_MESSAGE = (
    "Please specify the expense metric, grouping, report status, and reporting period."
)

GENERAL_CLARIFICATION_MESSAGE = (
    "Please provide an approved aggregate expense question with a department, "
    "metric, report status, and reporting period."
)

DESTRUCTIVE_REFUSAL_MESSAGE = (
    "I cannot perform database writes or destructive operations. Analytics access is read-only."
)

RESTRICTED_DATA_REFUSAL_MESSAGE = (
    "I cannot provide employee-level merchant activity. "
    "Only approved aggregate analytics are supported."
)

SYSTEM_PROMPT = """You generate one narrow PostgreSQL analytics query.

Rules:
1. Return exactly the requested JSON structure.
2. Generate exactly one SELECT statement.
3. Use only the analytics schema and the supplied tables and columns.
4. Do not use SELECT *, CTEs, subqueries, comments, or database functions
   outside ordinary aggregation and date extraction.
5. Do not access employee names, email addresses, salaries, merchants, or
   employee-level activity.
6. Use explicit table aliases and qualified columns.
7. Filter paid reports using expense_reports.status = 'paid'.
8. Use an inclusive start date and exclusive end date for calendar years.
9. Do not invent tables or columns.
10. For this approved question, return exactly these expressions:
    - departments.name AS department
    - COUNT(DISTINCT expense_reports.id) AS report_count
    - SUM(expense_items.amount) AS total_usd
11. Filter the calendar year using expense_reports.submitted_date, not trip
    dates, expense dates, or approval dates.
12. Group the result by departments.name.
"""

SCHEMA_CONTEXT = """Approved schema:

analytics.departments
- id
- code
- name
- cost_center
- is_active

analytics.employees
- id
- department_id
- employment_status

analytics.expense_reports
- id
- employee_id
- status
- submitted_date
- approved_date
- trip_start_date
- trip_end_date

analytics.expense_items
- id
- report_id
- expense_date
- category
- amount
- currency
- receipt_provided
- reimbursable
"""

EXPECTED_TABLES = {
    "departments",
    "employees",
    "expense_items",
    "expense_reports",
}

REQUIRED_LITERAL_VALUES = {
    "Engineering",
    "paid",
    "2025-01-01",
    "2026-01-01",
}

REQUIRED_RESULT_ALIASES = {
    "department",
    "report_count",
    "total_usd",
}

PROHIBITED_DATE_COLUMNS = {
    "approved_date",
    "trip_start_date",
    "trip_end_date",
    "expense_date",
}


def _validate_engineering_query_contract(sql: str) -> None:
    """Ensure SQL matches the approved question's semantic contract."""

    statement = sqlglot.parse_one(sql, read="postgres")

    table_aliases = {table.alias_or_name: table.name for table in statement.find_all(exp.Table)}

    literal_values = {str(literal.this) for literal in statement.find_all(exp.Literal)}
    missing_literals = REQUIRED_LITERAL_VALUES - literal_values

    if missing_literals:
        missing = ", ".join(sorted(missing_literals))
        raise SQLValidationError(f"generated SQL omitted required filters: {missing}")

    projections = {
        projection.alias: projection for projection in statement.expressions if projection.alias
    }
    missing_aliases = REQUIRED_RESULT_ALIASES - set(projections)

    if missing_aliases:
        missing = ", ".join(sorted(missing_aliases))
        raise SQLValidationError(f"generated SQL omitted required result columns: {missing}")

    def contains_column(
        expression: Any,
        *,
        table_name: str,
        column_name: str,
    ) -> bool:
        return any(
            column.name == column_name and table_aliases.get(column.table) == table_name
            for column in expression.find_all(exp.Column)
        )

    department_projection = projections["department"]

    if not contains_column(
        department_projection,
        table_name="departments",
        column_name="name",
    ):
        raise SQLValidationError("department must come from analytics.departments.name")

    report_count_projection = projections["report_count"]
    count_expression = report_count_projection.find(exp.Count)

    if (
        count_expression is None
        or count_expression.find(exp.Distinct) is None
        or not contains_column(
            count_expression,
            table_name="expense_reports",
            column_name="id",
        )
    ):
        raise SQLValidationError("report_count must use COUNT(DISTINCT expense_reports.id)")

    total_projection = projections["total_usd"]
    sum_expression = total_projection.find(exp.Sum)

    if sum_expression is None or not contains_column(
        sum_expression,
        table_name="expense_items",
        column_name="amount",
    ):
        raise SQLValidationError("total_usd must use SUM(expense_items.amount)")

    if any(column.name in PROHIBITED_DATE_COLUMNS for column in statement.find_all(exp.Column)):
        raise SQLValidationError("the approved question must use submitted_date for its date range")

    submitted_date_references = [
        column
        for column in statement.find_all(exp.Column)
        if column.name == "submitted_date" and table_aliases.get(column.table) == "expense_reports"
    ]

    if len(submitted_date_references) < 2:
        raise SQLValidationError(
            "the approved question requires lower and upper submitted_date bounds"
        )

    group = statement.args.get("group")

    if group is None or not contains_column(
        group,
        table_name="departments",
        column_name="name",
    ):
        raise SQLValidationError("generated SQL must group by departments.name")


def _format_engineering_answer(
    rows: list[dict[str, Any]],
) -> str:
    """Format a response only from verified database results."""

    if len(rows) != 1:
        raise RuntimeError("Engineering spend query returned an unexpected row count")

    row = rows[0]
    department = row.get("department")
    report_count = row.get("report_count")
    total_value = row.get("total_usd")

    if department != "Engineering":
        raise RuntimeError("query returned an unexpected department")

    if not isinstance(report_count, int):
        raise RuntimeError("query returned an invalid report count")

    if not isinstance(total_value, Decimal):
        raise RuntimeError("query returned an invalid monetary total")

    return (
        f"Engineering had {report_count} paid expense reports totaling ${total_value:,.2f} in 2025."
    )


def answer_approved_engineering_question(
    question: str,
    *,
    llm_provider: LLMProvider,
    engine: Engine,
) -> AnalyticsAnswer:
    """Generate, validate, execute and explain one approved question."""

    normalized_question = question.strip()

    if normalized_question != APPROVED_ENGINEERING_QUESTION:
        raise ValueError("question is outside this approved analytics operation")

    started_at = perf_counter()
    user_prompt = f"""{SCHEMA_CONTEXT}



Approved question:
{normalized_question}

Required result contract:
- department: analytics.departments.name
- report_count: COUNT(DISTINCT analytics.expense_reports.id)
- total_usd: SUM(analytics.expense_items.amount)
- use expense_reports.submitted_date for the 2025 date range
- group by departments.name
- return exactly one aggregate row for Engineering

Return JSON containing:
- sql: one PostgreSQL SELECT statement
"""

    generation = llm_provider.generate(
        system_prompt=SYSTEM_PROMPT,
        user_prompt=user_prompt,
        response_format=SQLProposal.model_json_schema(),
    )

    proposal = SQLProposal.model_validate_json(generation.content)
    validated = validate_sql(proposal.sql)

    if set(validated.tables) != EXPECTED_TABLES:
        raise SQLValidationError("generated SQL did not use the required analytics tables")

    _validate_engineering_query_contract(validated.sql)

    execution = execute_validated_sql(
        validated,
        engine=engine,
    )
    answer = _format_engineering_answer(execution.rows)

    return AnalyticsAnswer(
        status="answered",
        answer=answer,
        sql=validated.sql,
        rows=execution.rows,
        llm_model=generation.model,
        prompt_tokens=generation.prompt_tokens,
        completion_tokens=generation.completion_tokens,
        total_latency_ms=round(
            (perf_counter() - started_at) * 1000,
            3,
        ),
    )


def answer_analytics_question(
    question: str,
    *,
    llm_provider: LLMProvider,
    engine: Engine,
) -> AnalyticsAnswer:
    """Route an analytics request through controlled application policy."""

    normalized_question = question.strip()

    if not normalized_question:
        raise ValueError("question must not be empty")

    started_at = perf_counter()

    if normalized_question == DESTRUCTIVE_REQUEST:
        return AnalyticsAnswer(
            status="refusal",
            answer=DESTRUCTIVE_REFUSAL_MESSAGE,
            total_latency_ms=round(
                (perf_counter() - started_at) * 1000,
                3,
            ),
        )

    if normalized_question == RESTRICTED_DATA_REQUEST:
        return AnalyticsAnswer(
            status="refusal",
            answer=RESTRICTED_DATA_REFUSAL_MESSAGE,
            total_latency_ms=round(
                (perf_counter() - started_at) * 1000,
                3,
            ),
        )

    if normalized_question == AMBIGUOUS_QUARTER_QUESTION:
        return AnalyticsAnswer(
            status="clarification",
            answer=QUARTER_CLARIFICATION_MESSAGE,
            total_latency_ms=round(
                (perf_counter() - started_at) * 1000,
                3,
            ),
        )

    if normalized_question == AMBIGUOUS_EXPENSE_QUESTION:
        return AnalyticsAnswer(
            status="clarification",
            answer=EXPENSE_CLARIFICATION_MESSAGE,
            total_latency_ms=round(
                (perf_counter() - started_at) * 1000,
                3,
            ),
        )

    if normalized_question == APPROVED_ENGINEERING_QUESTION:
        return answer_approved_engineering_question(
            normalized_question,
            llm_provider=llm_provider,
            engine=engine,
        )

    return AnalyticsAnswer(
        status="clarification",
        answer=GENERAL_CLARIFICATION_MESSAGE,
        total_latency_ms=round(
            (perf_counter() - started_at) * 1000,
            3,
        ),
    )

from dataclasses import dataclass
from time import perf_counter
from typing import Any

import sqlglot
from sqlalchemy import Engine, text
from sqlglot import expressions as exp
from sqlglot.errors import ParseError

from enterprise_knowledge_analytics_agent.persistence.database import (
    create_database_engine,
)

MAX_RESULT_ROWS = 100
STATEMENT_TIMEOUT_MS = 3_000
ANALYTICS_READER_ROLE = "enterprise_agent_analytics_reader"

ALLOWED_COLUMNS: dict[str, frozenset[str]] = {
    "departments": frozenset(
        {
            "id",
            "code",
            "name",
            "cost_center",
            "is_active",
        }
    ),
    "employees": frozenset(
        {
            "id",
            "department_id",
            "employment_status",
        }
    ),
    "expense_reports": frozenset(
        {
            "id",
            "employee_id",
            "status",
            "submitted_date",
            "approved_date",
            "trip_start_date",
            "trip_end_date",
        }
    ),
    "expense_items": frozenset(
        {
            "id",
            "report_id",
            "expense_date",
            "category",
            "amount",
            "currency",
            "receipt_provided",
            "reimbursable",
        }
    ),
}

RESTRICTED_COLUMNS = frozenset(
    {
        "annual_salary",
        "work_email",
        "display_name",
        "employee_number",
        "merchant",
        "description",
    }
)


class SQLValidationError(ValueError):
    """Raised when generated SQL violates the analytics safety policy."""


@dataclass(frozen=True)
class ValidatedSQL:
    """SQL that has passed application-level AST validation."""

    sql: str
    tables: tuple[str, ...]
    columns: tuple[str, ...]
    row_limit: int


@dataclass(frozen=True)
class SQLExecutionResult:
    """Serializable result of one validated read-only query."""

    columns: list[str]
    rows: list[dict[str, Any]]
    row_count: int
    elapsed_ms: float


def validate_sql(
    sql: str,
    *,
    max_result_rows: int = MAX_RESULT_ROWS,
) -> ValidatedSQL:
    """Parse and validate one narrow, read-only analytics SELECT."""

    normalized_sql = sql.strip()

    if not normalized_sql:
        raise SQLValidationError("SQL must not be empty")

    if max_result_rows < 1:
        raise ValueError("max_result_rows must be at least 1")

    try:
        statements = sqlglot.parse(normalized_sql, read="postgres")
    except ParseError as error:
        raise SQLValidationError("SQL could not be parsed") from error

    if len(statements) != 1:
        raise SQLValidationError("exactly one SQL statement is allowed")

    statement = statements[0]

    if not isinstance(statement, exp.Select):
        raise SQLValidationError("only SELECT statements are allowed")

    if statement.args.get("with_") is not None:
        raise SQLValidationError("CTEs are not allowed")

    if statement.args.get("into") is not None:
        raise SQLValidationError("SELECT INTO is not allowed")

    if statement.args.get("locks"):
        raise SQLValidationError("locking SELECT statements are not allowed")

    if statement.find(exp.Subquery) is not None:
        raise SQLValidationError("subqueries are not allowed")

    if statement.find(exp.Star) is not None:
        raise SQLValidationError("wildcard selection is not allowed")

    if statement.find(exp.Anonymous) is not None:
        raise SQLValidationError("unapproved SQL functions are not allowed")

    tables = list(statement.find_all(exp.Table))

    if not tables:
        raise SQLValidationError("query must reference an approved analytics table")

    aliases: dict[str, str] = {}
    referenced_tables: set[str] = set()

    for table in tables:
        table_name = table.name
        schema_name = table.db

        if schema_name != "analytics":
            raise SQLValidationError("all tables must use the analytics schema")

        if table_name not in ALLOWED_COLUMNS:
            raise SQLValidationError(f"table is not allowlisted: {table_name}")

        referenced_tables.add(table_name)
        aliases[table.alias_or_name] = table_name
        aliases[table_name] = table_name

    referenced_columns: set[str] = set()

    for column in statement.find_all(exp.Column):
        column_name = column.name

        if column_name in RESTRICTED_COLUMNS:
            raise SQLValidationError(f"column is restricted: {column_name}")

        table_reference = column.table

        if table_reference:
            table_name = aliases.get(table_reference)

            if table_name is None:
                raise SQLValidationError(f"unknown table alias: {table_reference}")

            if column_name not in ALLOWED_COLUMNS[table_name]:
                raise SQLValidationError(f"column is not allowlisted: {table_name}.{column_name}")
        else:
            matching_tables = [
                table_name
                for table_name in referenced_tables
                if column_name in ALLOWED_COLUMNS[table_name]
            ]

            if len(matching_tables) != 1:
                raise SQLValidationError(
                    f"unqualified column is unknown or ambiguous: {column_name}"
                )

        referenced_columns.add(column_name)

    limit = statement.args.get("limit")

    if limit is None:
        statement = statement.limit(max_result_rows)
        row_limit = max_result_rows
    else:
        limit_expression = limit.expression

        if not isinstance(limit_expression, exp.Literal):
            raise SQLValidationError("LIMIT must be an integer literal")

        try:
            row_limit = int(limit_expression.this)
        except (TypeError, ValueError) as error:
            raise SQLValidationError("LIMIT must be an integer literal") from error

        if row_limit < 1 or row_limit > max_result_rows:
            raise SQLValidationError(f"LIMIT must be between 1 and {max_result_rows}")

    return ValidatedSQL(
        sql=statement.sql(dialect="postgres"),
        tables=tuple(sorted(referenced_tables)),
        columns=tuple(sorted(referenced_columns)),
        row_limit=row_limit,
    )


def execute_validated_sql(
    validated_sql: ValidatedSQL,
    *,
    engine: Engine | None = None,
    statement_timeout_ms: int = STATEMENT_TIMEOUT_MS,
) -> SQLExecutionResult:
    """Execute validated SQL under read-only database safeguards."""

    if statement_timeout_ms < 1:
        raise ValueError("statement_timeout_ms must be at least 1")

    resolved_engine = engine or create_database_engine()
    owns_engine = engine is None
    started_at = perf_counter()

    try:
        with resolved_engine.connect() as connection:
            transaction = connection.begin()

            try:
                connection.execute(text("SET TRANSACTION READ ONLY"))
                connection.execute(text(f"SET LOCAL ROLE {ANALYTICS_READER_ROLE}"))
                connection.execute(
                    text(f"SET LOCAL statement_timeout = '{statement_timeout_ms}ms'")
                )

                result = connection.execute(text(validated_sql.sql))
                rows = [dict(row) for row in result.mappings().all()]
                columns = list(result.keys())
            finally:
                transaction.rollback()

        return SQLExecutionResult(
            columns=columns,
            rows=rows,
            row_count=len(rows),
            elapsed_ms=round(
                (perf_counter() - started_at) * 1000,
                3,
            ),
        )
    finally:
        if owns_engine:
            resolved_engine.dispose()

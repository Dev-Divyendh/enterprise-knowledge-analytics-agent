import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from enterprise_knowledge_analytics_agent.persistence.models.base import (
    Base,
    TimestampMixin,
)


class Department(TimestampMixin, Base):
    """A fictional organizational department."""

    __tablename__ = "departments"
    __table_args__ = (
        UniqueConstraint("code", name="uq_departments_code"),
        {"schema": "analytics"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    code: Mapped[str] = mapped_column(String(20), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    cost_center: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )


class Employee(TimestampMixin, Base):
    """A synthetic employee used only for portfolio analytics."""

    __tablename__ = "employees"
    __table_args__ = (
        UniqueConstraint("employee_number", name="uq_employees_employee_number"),
        {"schema": "analytics"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    employee_number: Mapped[str] = mapped_column(String(30), nullable=False)
    department_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("analytics.departments.id", ondelete="RESTRICT"),
        nullable=False,
    )
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)
    job_title: Mapped[str] = mapped_column(String(100), nullable=False)
    hire_date: Mapped[date] = mapped_column(Date, nullable=False)
    employment_status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="active",
        server_default="active",
    )
    work_email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    annual_salary: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)


class ExpenseReport(TimestampMixin, Base):
    """A business-expense report submitted by a synthetic employee."""

    __tablename__ = "expense_reports"
    __table_args__ = (
        UniqueConstraint("report_number", name="uq_expense_reports_report_number"),
        CheckConstraint(
            "trip_end_date IS NULL OR trip_start_date IS NULL OR trip_end_date >= trip_start_date",
            name="trip_date_range_valid",
        ),
        CheckConstraint(
            "status IN ('draft', 'submitted', 'approved', 'rejected', 'paid')",
            name="status_allowed",
        ),
        Index("ix_expense_reports_employee", "employee_id"),
        Index("ix_expense_reports_status_date", "status", "submitted_date"),
        {"schema": "analytics"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    report_number: Mapped[str] = mapped_column(String(30), nullable=False)
    employee_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("analytics.employees.id", ondelete="RESTRICT"),
        nullable=False,
    )
    purpose: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="submitted",
        server_default="submitted",
    )
    submitted_date: Mapped[date] = mapped_column(Date, nullable=False)
    approved_date: Mapped[date | None] = mapped_column(Date)
    trip_start_date: Mapped[date | None] = mapped_column(Date)
    trip_end_date: Mapped[date | None] = mapped_column(Date)


class ExpenseItem(TimestampMixin, Base):
    """One individual expense belonging to an expense report."""

    __tablename__ = "expense_items"
    __table_args__ = (
        CheckConstraint("amount > 0", name="amount_positive"),
        CheckConstraint(
            "category IN "
            "('airfare', 'hotel', 'meals', 'ground_transport', 'mileage', "
            "'supplies', 'other')",
            name="category_allowed",
        ),
        CheckConstraint("char_length(currency) = 3", name="currency_length_three"),
        Index("ix_expense_items_report", "report_id"),
        Index("ix_expense_items_category_date", "category", "expense_date"),
        {"schema": "analytics"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    report_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("analytics.expense_reports.id", ondelete="CASCADE"),
        nullable=False,
    )
    expense_date: Mapped[date] = mapped_column(Date, nullable=False)
    category: Mapped[str] = mapped_column(String(30), nullable=False)
    merchant: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
        default="USD",
        server_default="USD",
    )
    receipt_provided: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )
    reimbursable: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )
